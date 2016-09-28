import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import LabelStatistics
from LabelStatistics import LabelStatistics,LabelStatisticsWidget,LabelStatisticsLogic,LabelStatisticsTest
import QCLib
import numpy
import vtk.util.numpy_support as nps

#
# LabelStatisticsExt
#

class LabelStatisticsExt(LabelStatistics):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Label Statistics Extension" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Quantification","QC"]
    self.parent.dependencies = []
    self.parent.contributors = ["Gina Belmonte (AOUS)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    Add histogram chart to Label Statistics
    """
    self.parent.acknowledgementText = ""

#
# LabelStatisticsExtWidget
#

class LabelStatisticsExtWidget(LabelStatisticsWidget):

  def setup(self):
    LabelStatisticsWidget.setup(self)

    self.chartIgnoreZero.checked = True

    self.chartNormalize = qt.QCheckBox()
    self.chartNormalize.setText('Normalize')
    self.chartNormalize.checked = False
    self.chartNormalize.setToolTip('Normalize distributions')
    self.chartFrame.layout().addWidget(self.chartNormalize)
    
    self.chartOptions = ("Count", "Volume mm^3", "Volume cc", "Min", "Max", "Mean", "StdDev", "Distribution")
    self.chartOption.clear()
    self.chartOption.addItems(self.chartOptions)
    self.chartOption.currentIndex=(len(self.chartOptions)-1)
    self.chartNormalize.enabled = True
    self.chartButton.connect('clicked()', self.onChart)
    self.chartOption.connect('currentIndexChanged(int)',self.onChartOption)

    self.histFrame = qt.QGroupBox()
    self.histFrame.setTitle("Histogram")
    self.histFrame.setToolTip('Rebin distribution')
    self.histFrame.checkable=True
    self.histFrame.checked=False
    self.histFrame.enabled=False
    histLay = qt.QFormLayout(self.histFrame)
    self.parent.layout().removeWidget(self.chartFrame)
    self.parent.layout().removeWidget(self.exportToTableButton)
    self.parent.layout().addWidget(self.histFrame)
    self.parent.layout().addWidget(self.chartFrame)    
    self.parent.layout().addWidget(self.exportToTableButton)
    self.histFrame.connect('stateChanged(int)',self.onHistCheck)

    # self.hist = qt.QCheckBox()
    # self.hist.setText('Histogram')
    # self.hist.checked = False
    # self.hist.enabled = True
    # self.hist.setToolTip('Rebin distribution')
    # self.histFrame.layout().addWidget(self.hist)
    # self.hist.connect('stateChanged(int)',self.onHistCheck)

    NBlay=qt.QHBoxLayout()
    self.FBRB=qt.QRadioButton()
    self.FBRB.setText("FB")
    self.FBRB.setToolTip("w=2*IQR/N^(1/3)")
    self.FBRB.checked=True
    NBlay.addStretch(1)
    NBlay.addWidget(self.FBRB)
    self.RiceRB=qt.QRadioButton()
    self.RiceRB.setText("Rice")
    self.RiceRB.setToolTip("nb=2*N^(1/3)")
    NBlay.addStretch(1)
    NBlay.addWidget(self.RiceRB)
    self.DoaneRB=qt.QRadioButton()
    self.DoaneRB.setText("Doane")
    self.DoaneRB.setToolTip("nb=1+log2(N)+log2(1+abs(g1)/sg1)")
    NBlay.addStretch(1)
    NBlay.addWidget(self.DoaneRB)
    self.ManualRB=qt.QRadioButton()
    self.ManualRB.setText("Manual")
    self.ManualRB.connect("toggled(bool)",self.onHistCheck)
    NBlay.addStretch(1)
    NBlay.addWidget(self.ManualRB)

    self.nbinsSB=qt.QSpinBox()
    self.nbinsSB.minimum=1
    self.nbinsSB.maximum=10000
    self.nbinsSB.value=100
    self.nbinsSB.enabled=False
    NBlay.addWidget(self.nbinsSB)
    NBlay.addStretch(1)
    histLay.addRow("N. bins: ",NBlay)

    self.applyButton.connect('clicked()', self.onApply)

    # Add vertical spacer
    self.parent.layout().addStretch(5)

  def onApply(self):
    LabelStatisticsWidget.onApply(self)
    self.onChartOption(self.chartOption.currentIndex)

  def onChartOption(self,opt):
    self.chartNormalize.enabled = (opt==(len(self.chartOptions)-1))
    self.histFrame.enabled = (opt==(len(self.chartOptions)-1))
    self.onHistCheck()

  def onHistCheck(self):
    self.nbinsSB.enabled = self.histFrame.checked and self.histFrame.enabled and self.ManualRB.checked

  def onChart(self):
    """chart the label statistics
    """
    valueToPlot = self.chartOptions[self.chartOption.currentIndex]
    ignoreZero = self.chartIgnoreZero.checked
    normalize = self.chartNormalize.checked
    if self.histFrame.checked:
      if self.FBRB.checked:
        nbins="FB"
      elif self.RiceRB.checked:
        nbins="Rice"
      elif self.DoaneRB.checked:
        nbins="Doane"
      else:
        nbins = self.nbinsSB.value
    else:
      nbins=-1
    self.logic = LabelStatisticsExtLogic(self.grayscaleNode, self.labelNode)
    self.logic.createStatsChart(self.labelNode,valueToPlot,ignoreZero,normalize,nbins)

#
# LabelStatisticsExtLogic
#

class LabelStatisticsExtLogic(LabelStatisticsLogic):
  def __init__(self, grayscaleNode, labelNode, colorNode=None, nodeBaseName=None, fileName=None):
    LabelStatisticsLogic.__init__(self, grayscaleNode, labelNode, colorNode=None, nodeBaseName=None, fileName=None)
    self.grayscaleNode=grayscaleNode

  def createStatsChart(self, labelNode, valueToPlot, ignoreZero=False, normalize=False,nbins=-1):
    if valueToPlot != "Distribution":
      LabelStatisticsLogic.createStatsChart(self, labelNode, valueToPlot, ignoreZero)
    else:
      layoutNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
      layoutNodes.SetReferenceCount(layoutNodes.GetReferenceCount()-1)
      layoutNodes.InitTraversal()
      layoutNode = layoutNodes.GetNextItemAsObject()
      layoutNode.SetViewArrangement(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalQuantitativeView)

      chartViewNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
      chartViewNodes.SetReferenceCount(chartViewNodes.GetReferenceCount()-1)
      chartViewNodes.InitTraversal()
      chartViewNode = chartViewNodes.GetNextItemAsObject()

      chartNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())

      displayNode = self.labelNode.GetDisplayNode()
      colorNode = displayNode.GetColorNode()
      color=numpy.full(4,0)

      #arrayNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
      #array = arrayNode.GetArray()
      samples = len(self.labelStats["Labels"])
      qu=QCLib.QCUtil()

      rect=qu.minRectangle(labelNode)
      ROI=labelNode.GetImageData()
      nslices=ROI.GetDimensions()[2] #3D Volumes only
      im=self.grayscaleNode.GetImageData()

      s=[numpy.Inf,-numpy.Inf]
      start=0
      if ignoreZero:
        start=1

      for ln in range(start,samples):
        l=self.labelStats["Labels"][ln]
        min=self.labelStats[l,"Min"]
        max=self.labelStats[l,"Max"]
        if min<s[0]:
          s[0]=min
        if max>s[1]:
          s[1]=max

      sr=range(int(s[0]),int(s[1])+1)

      distr={}
      cont={}
      for sl in range(nslices):
        if ignoreZero:
            xmin=rect['xmin'][sl]
            xmax=rect['xmax'][sl]
            ymin=rect['ymin'][sl]
            ymax=rect['ymax'][sl]
        else:
          xmin=0
          xmax=ROI.GetDimensions()[0]
          ymin=0
          ymax=ROI.GetDimensions()[1]

        for x in range(xmin,xmax+1):
          for y in range(ymin,ymax+1):
            label=ROI.GetScalarComponentAsDouble(x,y,sl,0)

            if not (ignoreZero and label == 0): #TODO : use numpy.histogram
              val=im.GetScalarComponentAsDouble(x,y,sl,0)
              try:
                dslab=distr[label]
              except: #TODO: errorcode
                distr[label]=numpy.full(self.labelStats[label,"Count"],0)
                dslab=distr[label]
                cont[label]=-1

              cont[label]=cont[label]+1
              dslab[cont[label]]=val

      dx=numpy.diff(sr[0:2])[0]
      for n in range(samples):
        label=self.labelStats["Labels"][n]
        if not (ignoreZero and label == 0):
          if nbins=="FB":
            #Freedman Diaconis Estimator
            IQR=numpy.percentile(distr[label],75)-numpy.percentile(distr[label],25)
            bnw=2*IQR/numpy.power(distr[label].size,1.0/3.0)
            nb=int((s[1]-s[0])/bnw)
          elif nbins=="Rice":
            #Rice
            nb=int(2*numpy.power(distr[label].size,1.0/3.0))
          elif nbins=="Doane":
            #Doane
            mu=numpy.mean(distr[label])
            std=numpy.std(distr[label])
            g1=numpy.mean(numpy.power((distr[label]-mu)/float(std),3))
            n=distr[label].size
            sg1=numpy.sqrt(float(6*(n-2))/float(((n+1)*(n+3))))
            nb=int(1+numpy.log2(n)+numpy.log2(1+numpy.abs(g1)/sg1))
          elif nbins<=0:
            nb=int(s[1]-s[0]+1) #TODO: if is not integer?
          else:
            #Manual
            nb=nbins
            
          if nbins>0:
            nm="-hist-"+str(nb)
          else:
            nm=""
          name=colorNode.GetColorName(label) + "-" + self.grayscaleNode.GetName() + nm

          ntuple=nb
          print "ciccio " + str(label) + " " + str(nb)
          hst,bins=numpy.histogram(distr[label],bins=nb,range=[s[0],s[1]],density=normalize)

          arrayNode = slicer.mrmlScene.GetNodesByClassByName("vtkMRMLDoubleArrayNode",name).GetItemAsObject(0)

          if not arrayNode:
            arrayNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
            arrayNode.SetName(name)

          arrayD = arrayNode.GetArray()

          arrayD.SetNumberOfComponents(2)
          arrayD.SetNumberOfTuples(ntuple)

          for n in range(ntuple):
            arrayD.SetComponent(n, 0, bins[n]) #TODO
            arrayD.SetComponent(n, 1, hst[n])
            
          state = chartNode.StartModify()
          chartNode.AddArray(name, arrayNode.GetID())
          chartViewNode.SetChartNodeID(chartNode.GetID())
          chartNode.SetProperty('default', 'title', 'Label Statistics')
          chartNode.SetProperty('default', 'xAxisLabel', 'Values')
          chartNode.SetProperty('default', 'yAxisLabel', valueToPlot)
          chartNode.SetProperty('default', 'type', 'Line');
          chartNode.SetProperty('default', 'xAxisType', 'quantitative')
          chartNode.SetProperty('default', 'yAxisType', 'quantitative')
          chartNode.SetProperty('default', 'showLegend', 'on')
          colorNode.GetColor(label,color)
          col='#'+str(hex(color[0]*255)[2:4])+str(hex(color[1]*255)[2:4])+str(hex(color[2]*255)[2:4])
          chartNode.SetProperty(name,'color',col)
          chartNode.EndModify(state)
        

class LabelStatisticsExtTest(LabelStatisticsTest):
  pass
