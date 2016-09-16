import os
import unittest
from __main__ import vtk, qt, ctk, slicer
import QCLib

#
# VolumeStatistics
#

class VolumeStatistics:
  def __init__(self, parent):
    parent.title = "Volume Statistics"
    parent.categories = ["QC.Process"]
    parent.dependencies = []
    parent.contributors = ["Gina Belmonte(AOUS)"]
    parent.helpText = """
    Volume and area slice calculator
    """
    parent.acknowledgementText = ""
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['VolumeStatistics'] = self.runTest

  def runTest(self):
    tester = VolumeStatisticsTest()
    tester.runTest()

#
# qVolumeStatisticsWidget
#

class VolumeStatisticsWidget(QCLib.genericPanel):
  def __init__(self, parent = None):
    QCLib.genericPanel.__init__(self,parent)

    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    QCLib.genericPanel.setup(self)

    applicationLogic = slicer.app.applicationLogic()
    selectionNode = applicationLogic.GetSelectionNode()
    selectionNode.SetReferenceActiveVolumeID(None)
    selectionNode.SetReferenceActiveLabelVolumeID(None)
    selectionNode.SetReferenceSecondaryVolumeID(None)
    applicationLogic.PropagateVolumeSelection(0)

    self.volumes.text = "First Volume"
    volumeLayout=self.volumes.layout()
    for child in range(1,self.volumes.children().__len__()):
      self.volumes.children()[child].visible=False

    self.firstSelector = slicer.qMRMLNodeComboBox()
    self.firstSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.firstSelector.selectNodeUponCreation = False
    self.firstSelector.addEnabled = False
    self.firstSelector.removeEnabled = False
    self.firstSelector.noneEnabled = True
    self.firstSelector.showHidden = False
    self.firstSelector.showChildNodeTypes = False
    self.firstSelector.setMRMLScene( slicer.mrmlScene )
    self.firstSelector.setToolTip( "First Volume" )
    volumeLayout.addRow("First Volume: ", self.firstSelector)

    #
    # Second Volume collapsible button
    #
    parameterCollapsibleButton = ctk.ctkCollapsibleButton()
    parameterCollapsibleButton.text = "Optional Second Volume"
    self.framelayout.addWidget(parameterCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parameterCollapsibleButton)

    #
    # second volume selector
    #
    self.secondSelector = slicer.qMRMLNodeComboBox()
    self.secondSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.secondSelector.selectNodeUponCreation = False
    self.secondSelector.addEnabled = False
    self.secondSelector.removeEnabled = False
    self.secondSelector.noneEnabled = True
    self.secondSelector.editEnabled = False
    self.secondSelector.showHidden = False
    self.secondSelector.showChildNodeTypes = False
    self.secondSelector.setMRMLScene( slicer.mrmlScene )
    self.secondSelector.setToolTip( "Optional Second Volume" )
    self.secondSelector.enabled=False
    parametersFormLayout.addRow("Second Volume: ", self.secondSelector)

    #
    # Statistics Table collapsible button
    #
    statsCollapsibleButton = ctk.ctkCollapsibleButton()
    statsCollapsibleButton.text = "Statistics Table"
    self.framelayout.addWidget(statsCollapsibleButton)
    self.table=qt.QTableWidget(0,4)
    labels=['Slice','First: Volume & Area','Second: Volume & Area','Ratio: Second/First']
    self.table.setHorizontalHeaderLabels(labels)
    self.table.verticalHeader().setVisible(False)
    self.firstStats=None
    self.secondStats=None
    self.UpdateTable()

    statsCollapsibleButton.setLayout(qt.QVBoxLayout())
    statsCollapsibleButton.layout().addWidget(self.table)
    #statsLayout = qt.QHBoxLayout(parameterCollapsibleButton)
    #statsLayout.addWidget(self.table)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Calculate Volume(s) Statistics"
    self.applyButton.enabled = False
    self.framelayout.addWidget(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.firstSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectFirst)
    self.firstSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.secondSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectSecond)
    self.table.connect('currentCellChanged(int,int,int,int)', self.cellChanged)

    # Add vertical spacer
    self.framelayout.addStretch(1)
    
    count = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceCompositeNode')
    for n in xrange(count):
      compNode = slicer.mrmlScene.GetNthNodeByClass(n, 'vtkMRMLSliceCompositeNode')
      compNode.SetForegroundOpacity(0.5)

  def cellChanged(self,currentRow,currentColumn,previousRow,previousColumn):
    if currentRow>0:
      slnumt=self.table.item(currentRow,0).text()
      qu=QCLib.QCUtil()
      sn=qu.getSliceNode()

      if sn:
        try:
          slnum=int(slnumt)
          vol=self.firstSelector.currentNode()
          newoff=qu.getSliceOffsetFromIndex(slnum,vol)
          sn.SetSliceOffset(newoff)
        except:
          #sn.SetSliceOffset(orig)
          pass

  def onSelectSecond(self):
    applicationLogic = slicer.app.applicationLogic()
    selectionNode = applicationLogic.GetSelectionNode()
    if self.secondSelector.currentNode():
      selectionNode.SetReferenceSecondaryVolumeID(self.secondSelector.currentNode().GetID())
    else:
      selectionNode.SetReferenceSecondaryVolumeID(None)
    applicationLogic.PropagateVolumeSelection(0)

  def onSelectFirst(self):
    applicationLogic = slicer.app.applicationLogic()
    selectionNode = applicationLogic.GetSelectionNode()
    if self.firstSelector.currentNode():
      self.secondSelector.enabled = True
      selectionNode.SetReferenceActiveVolumeID(self.firstSelector.currentNode().GetID())
    else:
      selectionNode.SetReferenceActiveVolumeID(None)
      self.secondSelector.enabled = False
    applicationLogic.PropagateVolumeSelection(0)

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.firstSelector.currentNode()

  def onApplyButton(self):
    logic = VolumeStatisticsLogic()
    print("Calculate statistics")
    self.frame.enabled=False
    logic.run(self.firstSelector.currentNode(), self.secondSelector.currentNode())
    self.firstStats=logic.firstVolStats
    self.secondStats=logic.secondVolStats
    self.UpdateTable()
    self.frame.enabled=True

  def UpdateTable(self):
    firstlen=0
    if self.firstStats:
      firstlen=self.firstStats.__len__()
    secondlen=0
    if self.secondStats:
      secondlen=self.secondStats.__len__()

    len=max(firstlen,secondlen)

    self.table.setRowCount(len)
    
    self.tblits=[]
    if self.firstStats:
      for m in range(len):
        n=4*m
        if m<self.firstStats.__len__():
          self.tblits.append(qt.QTableWidgetItem(str(self.firstStats.keys()[m])))
          self.table.setItem(m,0,self.tblits[n])
          self.table.item(m,0).setFlags(33)
          
          self.tblits.append(qt.QTableWidgetItem(str(self.firstStats.values()[m])))
          self.table.setItem(m,1,self.tblits[n+1])
          self.table.item(m,1).setFlags(33)
        else:
          for j in range(2):
            self.tblits.append(None)

        if self.secondStats and m<self.secondStats.__len__():
          self.tblits.append(qt.QTableWidgetItem(str(self.secondStats.values()[m])))
          self.table.setItem(m,2,self.tblits[n+2])
          self.table.item(m,2).setFlags(33)

          if m<self.firstStats.__len__() and self.firstStats.values()[m]!=0:
            self.tblits.append(qt.QTableWidgetItem(str(float(self.secondStats.values()[m])/float(self.firstStats.values()[m]))))
            self.table.setItem(m,3,self.tblits[n+3])
            self.table.item(m,3).setFlags(33)
          else:
            self.tblits.append(None)
        else:
          for j in range(2):
            self.tblits.append(None)

    if self.secondStats:
      self.chartRatios()

    self.table.resizeColumnsToContents()

  def chartRatios(self):
    ratiosAr = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
    ratiosArinv = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
    firstName=self.firstSelector.currentNode().GetName()
    secondName=self.secondSelector.currentNode().GetName()
    ratiosAr.SetName(firstName+"-"+secondName+"-ratios")
    ratiosArinv.SetName(firstName+"-"+secondName+"-inverse-ratios")

    arrayD = ratiosAr.GetArray()
    arrayDinv = ratiosArinv.GetArray()

    arrayD.SetNumberOfTuples(self.table.rowCount)
    arrayDinv.SetNumberOfTuples(self.table.rowCount)

    for n in range(self.table.rowCount):
      if self.table.item(n,3):
        arrayD.SetComponent(n, 0, n)
        arrayDinv.SetComponent(n, 0, n)
        arrayD.SetComponent(n, 1, float(self.table.item(n,3).text()))
        arrayDinv.SetComponent(n, 1, float(self.table.item(self.table.rowCount-1-n,3).text()))

    layoutNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
    layoutNodes.SetReferenceCount(layoutNodes.GetReferenceCount()-1)
    layoutNodes.InitTraversal()
    layoutNode = layoutNodes.GetNextItemAsObject()
    layoutNode.SetViewArrangement(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpQuantitativeView)

    chartViewNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
    chartViewNodes.SetReferenceCount(chartViewNodes.GetReferenceCount()-1)
    chartViewNodes.InitTraversal()
    chartViewNode = chartViewNodes.GetNextItemAsObject()

    chartNode = slicer.mrmlScene.GetNodesByClassByName("vtkMRMLChartNode","Ratios").GetItemAsObject(0)
    if not chartNode:
      chartNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
      chartNode.SetName("Ratios")

      print("set properties")

      chartNode.SetProperty('default', 'title', 'Ratios')
      chartNode.SetProperty('default', 'xAxisLabel', 'slice')
      chartNode.SetProperty('default', 'yAxisLabel', 'Ratio')
      chartNode.SetProperty('default', 'type', 'Line')
      chartNode.SetProperty('default', 'showLegend', 'on')
      chartNode.SetProperty('default', 'Markers', 'on')

    chartViewNode.SetChartNodeID(chartNode.GetID())

    chartNode.AddArray("Ratio", ratiosAr.GetID())
    chartNode.AddArray("Ratioinv", ratiosArinv.GetID())

#
# VolumeStatisticsLogic
#

class VolumeStatisticsLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  def hasImageData(self,volumeNode):
    """This is a dummy logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      print('no volume node')
      return False
    if volumeNode.GetImageData() == None:
      print('no image data')
      return False
    return True

  def run(self,firstVolume,secondVolume=None):
    """
    Volume statistics
    """

    slicer.util.delayDisplay('Calculating statistics')

    self.firstVolume=firstVolume
    self.secondVolume=secondVolume

    self.createStatistics()

    return True

  def createStatistics(self):
    qu=QCLib.QCUtil()
    self.firstVolStats=qu.getVolStatistics(self.firstVolume,qu.getVolumeMin(self.firstVolume))

    if self.secondVolume:
      self.secondVolStats=qu.getVolStatistics(self.secondVolume,qu.getVolumeMin(self.secondVolume))
    else:
      self.secondVolStats=None
      
