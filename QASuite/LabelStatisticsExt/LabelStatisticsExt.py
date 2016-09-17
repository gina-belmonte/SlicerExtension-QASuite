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

    self.histFrame = qt.QFrame()
    self.histFrame.setLayout(qt.QFormLayout())
    self.parent.layout().addWidget(self.histFrame)

    self.hist = qt.QCheckBox()
    self.hist.setText('Histogram')
    self.hist.checked = False
    self.hist.enabled = True
    self.hist.setToolTip('Rebin distribution')
    self.histFrame.layout().addWidget(self.hist)
    self.hist.connect('stateChanged(int)',self.onHistCheck)

    self.nbinsSB=qt.QSpinBox()
    self.nbinsSB.minimum=1
    self.nbinsSB.maximum=10000
    self.nbinsSB.value=100
    self.nbinsSB.enabled=False
    self.histFrame.layout().addRow("Number of bins: ",self.nbinsSB)

  def onChartOption(self,opt):
    self.chartNormalize.enabled = (opt==(len(self.chartOptions)-1))
    self.hist.enabled = (opt==(len(self.chartOptions)-1))
    self.nbinsSB.enabled = self.hist.checked and (opt==(len(self.chartOptions)-1))

  def onHistCheck(self):
    self.nbinsSB.enabled = self.hist.checked and self.hist.enabled

  def onChart(self):
    """chart the label statistics
    """
    valueToPlot = self.chartOptions[self.chartOption.currentIndex]
    ignoreZero = self.chartIgnoreZero.checked
    normalize = self.chartNormalize.checked
    nbins=-1
    if self.nbinsSB.enabled:
      nbins = self.nbinsSB.value
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

        cont={}
        for x in range(xmin,xmax+1):
          for y in range(ymin,ymax+1):
            label=ROI.GetScalarComponentAsDouble(x,y,sl,0)

            if not (ignoreZero and label == 0): #TODO : use numpy.histogram
              val=im.GetScalarComponentAsDouble(x,y,sl,0)
              try:
                  dslab=distr[label]
              except: #TODO: errorcode
                if nbins>0:
                  distr[label]=numpy.full(self.labelStats[label,"Count"],0)
                  dslab=distr[label]
                  cont[label]=-1
                else:
                  xr=s[1]-s[0]
                  distr[label]=numpy.full(xr+1,0)
                  dslab=distr[label]
                  
              if nbins>0:
                cont[label]=cont[label]+1
                dslab[cont[label]]=val
              else:
                dslab[val-s[0]]+=1 #TODO: only integer values for now

      dx=numpy.diff(sr[0:2])[0]
      for n in range(samples):
        label=self.labelStats["Labels"][n]
        if not (ignoreZero and label == 0):
          #name="Label-"+str(label)
          if nbins>0:
            nm="-hist"
          else:
            nm=""
          name=colorNode.GetColorName(label) + "-" + self.grayscaleNode.GetName() + nm
          if nbins>0:
            ntuple=nbins
          else:
            ntuple=len(distr[label])

          arrayNode = slicer.mrmlScene.GetNodesByClassByName("vtkMRMLDoubleArrayNode",name).GetItemAsObject(0)

          if not arrayNode:
            arrayNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
            arrayNode.SetName(name)

          arrayD = arrayNode.GetArray()

          arrayD.SetNumberOfComponents(2)
          arrayD.SetNumberOfTuples(ntuple)

          nrm=1
          if normalize:
            nrm=numpy.sum(distr[label]*dx)

          if nbins>0:
            # #Freedman Diaconis Estimator
            # IQR=numpy.percentile(distr[label],75)-numpy.percentile(distr[label],25)
            # bnw=2*IQR/numpy.power(distr[label].size,1.0/3.0)
            # nb=int((s[1]-s[0])/bnw)
            # #Rice
            # nb=int(2*numpy.power(distr[label].size,1.0/3.0))
            #Doane
            # mu=numpy.mean(distr[label])
            # std=numpy.std(distr[label])
            # g1=numpy.mean(numpy.power((distr[label]-mu)/float(std),3))
            # n=distr[label].size
            # sg1=numpy.sqrt(float(6*(n-2))/float(((n+1)*(n+3))))
            # nb=int(1+numpy.log2(n)+numpy.log2(1+numpy.abs(g1)/sg1))

            nb=nbins
            ntuple=nb
            print "ciccio " + str(label) + " " + str(nb)
            hst,bins=numpy.histogram(distr[label],bins=nb,range=[s[0],s[1]],density=normalize)

          for n in range(ntuple):
            if nbins>0:
              arrayD.SetComponent(n, 0, bins[n]) #TODO
              arrayD.SetComponent(n, 1, hst[n])
            else:
              arrayD.SetComponent(n, 0, sr[n])
              arrayD.SetComponent(n, 1, distr[label][n]/nrm)
            
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
