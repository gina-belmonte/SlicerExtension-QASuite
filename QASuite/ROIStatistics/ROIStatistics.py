import os
import QCLib
import unittest
from __main__ import vtk, qt, ctk, slicer

#
# ROIStatistics
#

class ROIStatistics:
  def __init__(self, parent):
    parent.title = "ROI Statistics and Uniformity"
    parent.categories = ["QC.Process"]
    parent.dependencies = []
    parent.contributors = ["Gina Belmonte (AOUS)"]
    parent.helpText = """
    Perform ROI statistics per slice
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
    slicer.selfTests['ROIStatistics'] = self.runTest

  def runTest(self):
    tester = ROIStatisticsTest()
    tester.runTest()

#
# qROIStatisticsWidget
#

class ROIStatisticsWidget(QCLib.genericPanel):
  def __init__(self, parent = None):
    QCLib.genericPanel.__init__(self,parent)

    self.stats=None
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

    #
    # ROI collapsible button
    #
    parameterCollapsibleButton = ctk.ctkCollapsibleButton()
    parameterCollapsibleButton.text = "ROI Volume"
    self.framelayout.addWidget(parameterCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parameterCollapsibleButton)

    #
    # ROI volume selector
    #
    self.ROISelector = slicer.qMRMLNodeComboBox()
    # self.ROISelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    # self.ROISelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    self.ROISelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
    self.ROISelector.selectNodeUponCreation = False
    self.ROISelector.addEnabled = False
    self.ROISelector.removeEnabled = False
    self.ROISelector.noneEnabled = True
    self.ROISelector.editEnabled = False
    self.ROISelector.showHidden = False
    self.ROISelector.showChildNodeTypes = False
    self.ROISelector.setMRMLScene( slicer.mrmlScene )
    self.ROISelector.setToolTip( "ROI Volume" )
    self.ROISelector.enabled=False
    parametersFormLayout.addRow("ROI Volume: ", self.ROISelector)

    #
    # Statistics Table collapsible button
    #
    statsCollapsibleButton = ctk.ctkCollapsibleButton()
    statsCollapsibleButton.text = "Statistics Table"
    self.framelayout.addWidget(statsCollapsibleButton)
    self.tabpanel=qt.QTabWidget()
    #self.table=qt.QTableWidget(0,7)
    self.labels=['Slice','Count','Mean','SD','Max','Min','U']
    #self.table.setHorizontalHeaderLabels(labels)
    #self.table.verticalHeader().setVisible(False)
    self.ROIStats=None
    self.UpdateTable()

    statsCollapsibleButton.setLayout(qt.QVBoxLayout())
    #statsCollapsibleButton.layout().addWidget(self.table)
    statsCollapsibleButton.layout().addWidget(self.tabpanel)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Calculate ROI Statistics"
    self.applyButton.enabled = False
    self.framelayout.addWidget(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.masterSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectMaster)
    self.masterSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.ROISelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectROI)
    self.ROISelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    #self.table.connect('currentCellChanged(int,int,int,int)', self.cellChanged)

    # Add vertical spacer
    self.framelayout.addStretch(1)
    
    # count = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceCompositeNode')
    # for n in xrange(count):
    #   compNode = slicer.mrmlScene.GetNthNodeByClass(n, 'vtkMRMLSliceCompositeNode')
    #   compNode.SetForegroundOpacity(0.0)

  def cleanup(self):
    pass

  def UpdateTable(self):
    if self.stats:
      numrois=self.stats.__len__()
      self.tbis=[]
      for roi in range(numrois):
        statROI=self.stats.values()[roi]
        len=statROI.__len__()

        table=self.tabpanel.widget(roi)
        table.setRowCount(len)

        #self.tbis[roi]=[]
        tblits=[]
        for m in range(len):
          n=7*m
          tblits.append(qt.QTableWidgetItem(str(statROI.keys()[m])))
          table.setItem(m,0,tblits[n])
          table.item(m,0).setFlags(33)

          statroi=statROI.values()[m]

          tblits.append(qt.QTableWidgetItem(str(statroi['count'])))
          table.setItem(m,1,tblits[n+1])
          table.item(m,1).setFlags(33)

          tblits.append(qt.QTableWidgetItem(str(statroi['mean'])))
          table.setItem(m,2,tblits[n+2])
          table.item(m,2).setFlags(33)

          tblits.append(qt.QTableWidgetItem(str(statroi['sd'])))
          table.setItem(m,3,tblits[n+3])
          table.item(m,3).setFlags(33)

          if statroi['count']>0:
            max=int(statroi['max'])
          else:
            max=0
          tblits.append(qt.QTableWidgetItem(str(max)))
          table.setItem(m,4,tblits[n+4])
          table.item(m,4).setFlags(33)

          if statroi['count']>0:
            min=int(statroi['min'])
          else:
            min=0
          tblits.append(qt.QTableWidgetItem(str(min)))
          table.setItem(m,5,tblits[n+5])
          table.item(m,5).setFlags(33)

          if max+min>0:
            U=1-(float(max-min)/float(max+min))
          else:
            U=0
          tblits.append(qt.QTableWidgetItem(str(U)))
          table.setItem(m,6,tblits[n+6])
          table.item(m,6).setFlags(33)

        self.tbis.append(tblits)

        table.resizeColumnsToContents()

  def itemChanged(self,prevItem,curItem):
    if curItem:
      table=curItem.tableWidget()
      row=curItem.row()
      col=curItem.column()
      self.cellChanged(table,row,col)

  def currCellChanged(self,row,col,prevrow,prevcol):
    table=self.tabpanel.currentWidget()
    self.cellChanged(table,row,col)

  def cellChanged(self,table,currentRow,currentColumn):
    if currentRow>=0:
      slnumt=table.item(currentRow,0).text()
      qu=QCLib.QCUtil()
      sn=qu.getSliceNode()

      if sn:
        try:
          slnum=int(slnumt)
          vol=self.masterSelector.currentNode()
          newoff=qu.getSliceOffsetFromIndex(slnum,vol)
          sn.SetSliceOffset(newoff)
        except:
          #sn.SetSliceOffset(orig)
          pass

  def onSelect(self):
    self.applyButton.enabled = self.masterSelector.currentNode() and self.ROISelector.currentNode()

  def onSelectMaster(self):
    applicationLogic = slicer.app.applicationLogic()
    selectionNode = applicationLogic.GetSelectionNode()
    master=self.masterSelector.currentNode()
    if master:
      self.ROISelector.enabled = True
      selectionNode.SetReferenceActiveVolumeID(self.masterSelector.currentNode().GetID())

      merge=self.ROISelector.currentNode()
      if merge:
        warnings = self.checkForVolumeWarnings(master,merge)
        if warnings != "":
          self.errorDialog( "Warning: %s" % warnings )
          self.ROISelector.setCurrentNode(None)
          selectionNode.SetReferenceActiveLabelVolumeID(None)
        else:
          selectionNode.SetReferenceActiveLabelVolumeID(self.ROISelector.currentNode().GetID())
    else:
      selectionNode.SetReferenceActiveVolumeID(None)
      self.ROISelector.enabled = False
    applicationLogic.PropagateVolumeSelection(0)

  def onSelectROI(self):
    applicationLogic = slicer.app.applicationLogic()
    selectionNode = applicationLogic.GetSelectionNode()
    master=self.masterSelector.currentNode()
    merge=self.ROISelector.currentNode()
    if merge:
      warnings = self.checkForVolumeWarnings(master,merge)
      if warnings != "":
        self.errorDialog( "Warning: %s" % warnings )
        self.ROISelector.setCurrentNode(None)
        selectionNode.SetReferenceActiveLabelVolumeID(None)
      else:
        ROI=self.ROISelector.currentNode()
        ROIim=ROI.GetImageData()
        ROIcol=ROI.GetDisplayNode().GetColorNode()
        lut=ROIcol.GetLookupTable()
        selectionNode.SetReferenceActiveLabelVolumeID(ROI.GetID())
        roinums=int(ROIim.GetScalarRange()[1])
        self.tabpanel.clear()
        for roi in range(1,roinums+1):
          rgb = lut.GetTableValue(roi)
          color = qt.QColor()
          color.setRgb(rgb[0]*255,rgb[1]*255,rgb[2]*255)
          idx=self.tabpanel.addTab(qt.QTableWidget(0,7),"ROI: " + ROIcol.GetColorName(roi) + "(" + str(roi) + ")")
          pix=qt.QPixmap(32,32)
          pix.fill(color)
          self.tabpanel.setTabIcon(idx,qt.QIcon(pix))
          self.tabpanel.widget(idx).setHorizontalHeaderLabels(self.labels)
          self.tabpanel.widget(idx).verticalHeader().setVisible(False)
          #self.tabpanel.widget(idx).connect('currentItemChanged(QTableWidgetItem,QTableWidgetItem)', self.itemChanged)
          self.tabpanel.widget(idx).connect('currentCellChanged(int,int,int,int)', self.currCellChanged)
    else:
      selectionNode.SetReferenceActiveLabelVolumeID(None)
    applicationLogic.PropagateVolumeSelection(0)

  def onApplyButton(self):
    applicationLogic = slicer.app.applicationLogic()
    selectionNode = applicationLogic.GetSelectionNode()
    master=self.masterSelector.currentNode()
    merge=self.ROISelector.currentNode()
    warnings = self.checkForVolumeWarnings(master,merge)
    if warnings != "":
      self.errorDialog( "Warning: %s" % warnings )
      self.ROISelector.setCurrentNode(None)
      selectionNode.SetReferenceActiveLabelVolumeID(None)
      applicationLogic.PropagateVolumeSelection(0)
    else:
      selectionNode.SetReferenceActiveVolumeID(master.GetID())
      selectionNode.SetReferenceActiveLabelVolumeID(merge.GetID())
      applicationLogic.PropagateVolumeSelection(0)
      logic = ROIStatisticsLogic()
      print("Perform ROI Statistics")
      self.frame.enabled=False
      logic.run(master,merge)
      self.stats=logic.stats
      self.UpdateTable()
      self.frame.enabled=True


#
# ROIStatisticsLogic
#

class ROIStatisticsLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  def run(self,inputVolume,roiVolume):
    """
    Perform ROI Statistics
    """

    slicer.util.delayDisplay('ROI Statistics')

    self.master=inputVolume
    self.ROI=roiVolume

    self.stats=self.getROIStats()

  def getROIStats(self):
    qu=QCLib.QCUtil()

    return qu.getROIstats(self.master,self.ROI)

    return True
