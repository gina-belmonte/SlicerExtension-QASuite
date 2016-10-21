import os
import unittest
from __main__ import vtk, qt, ctk, slicer
import QCLib

#
# EdgeDetect
#

class EdgeDetect:
  def __init__(self, parent):
    parent.title = "Edge Detection"
    parent.categories = ["QC.Process"]
    parent.dependencies = []
    parent.contributors = ["Gina Belmonte(AOUS)"]
    parent.helpText = """
    An edge detection module
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
    slicer.selfTests['EdgeDetect'] = self.runTest

  def runTest(self):
    tester = EdgeDetectTest()
    tester.runTest()

#
# qEdgeDetectWidget
#

class EdgeDetectWidget (QCLib.genericPanel):
  def __init__(self, parent = None):
    QCLib.genericPanel.__init__(self,parent)

    self.coln=slicer.mrmlScene.GetNodesByClassByName('vtkMRMLColorNode','GMBColorTable').GetItemAsObject(0)

    if not self.coln:
      self.coln=slicer.vtkMRMLColorTableNode()
      self.coln.SetName("GMBColorTable")
      self.coln.SetTypeToUser()
      self.coln.HideFromEditorsOff()
      self.coln.SetNumberOfColors(2)
      self.coln.SetColor(0,'bg',0,0,0)
      self.coln.SetColor(1,'fg',1,0,0)
      self.coln.SetOpacity(0,0)
      self.coln.SetOpacity(1,1)
      slicer.mrmlScene.AddNode(self.coln)

    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    QCLib.genericPanel.setup(self)

    #
    # Output Volume collapsible button
    #
    self.output = ctk.ctkCollapsibleButton(self.frame)
    self.output.setText("Output Volume")
    self.output.enabled=False
    self.framelayout.addWidget(self.output)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(self.output)

    #
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    #self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.outputSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
    #self.outputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = False
    self.outputSelector.renameEnabled = True
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene(slicer.mrmlScene)
    self.outputSelector.setToolTip("Output Volume")
    #self.outputSelector.enabled=False
    parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

    #algorithm selector
    self.algorithmSel = ctk.ctkComboBox()
    algorithms=["Canny","Sobel","Zero Crossing Based"]
    self.algorithmSel.addItems(algorithms)
    #self.algorithmSel.enabled=False
    self.algorithmSel.editable=False
    self.algorithmSel.setCurrentIndex(0)
    parametersFormLayout.addRow("Edge Detection Algorithm", self.algorithmSel)

    self.optionFrame=qt.QFrame()
    self.optionFrame.setLayout(qt.QFormLayout())
    self.optionFrame.enabled=False
    self.framelayout.addWidget(self.optionFrame)

    #variance slider
    self.varianceSlider = ctk.ctkSliderWidget()
    self.varianceSlider.minimum = 0
    self.varianceSlider.maximum = 100
    self.varianceSlider.setValue(2)
    #self.varianceSlider.enabled = False
    self.varianceSlider.setToolTip("Variance of the pre gaussian filter")
    self.optionFrame.layout().addRow("Variance", self.varianceSlider)

    #threshold slider
    self.threshSlider=ctk.ctkRangeWidget()
    self.threshSlider.minimum = 0
    self.threshSlider.maximum = 0
    self.threshSlider.setValues(0,0)
    #self.threshSlider.enabled=False
    self.threshSlider.setToolTip("Threshold of output volume")
    self.optionFrame.layout().addRow("Threshold", self.threshSlider)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the edge detection algotrithm"
    self.applyButton.enabled = False
    self.framelayout.addWidget(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.masterSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectInput)
    self.masterSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectOutput)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.algorithmSel.connect("currentIndexChanged(int)", self.setOptionEnabled)

    # Add vertical spacer
    self.layout.addStretch(1)

    count = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceCompositeNode')
    for n in xrange(count):
      compNode = slicer.mrmlScene.GetNthNodeByClass(n, 'vtkMRMLSliceCompositeNode')
      compNode.SetForegroundOpacity(1.0)

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.masterSelector.currentNode() and self.outputSelector.currentNode()

  def onSelectInput(self):
    master=self.masterSelector.currentNode()

    #self.algorithmSel.enabled=False
    #self.varianceSlider.enabled = False
    #self.threshSlider.enabled = False
    self.threshSlider.setValues(0,0)
    self.threshSlider.maximum = 0
    #self.outputSelector.enabled=False
    self.output.enabled=False
    self.optionFrame.enabled=False

    if master:
      self.threshSlider.maximum = master.GetImageData().GetScalarRange()[1]

      #self.algorithmSel.enabled=True
      #self.varianceSlider.enabled = True
      #self.threshSlider.enabled = True
      #self.outputSelector.enabled=True
      self.outputSelector.setCurrentNode(None)
      self.output.enabled=True
      self.setOptionEnabled()

  def setOptionEnabled(self):
    self.optionFrame.enabled=(self.algorithmSel.currentIndex!=1)
    self.varianceSlider.enabled=self.optionFrame.enabled
    self.threshSlider.enabled=(self.algorithmSel.currentIndex==0)

  def onSelectOutput(self):
    merge=self.outputSelector.currentNode()
    master=self.masterSelector.currentNode()

    if master and merge:
      if not merge.GetImageData():
        print("create Output Volume")
        imd=vtk.vtkImageData()

        mim=master.GetImageData()
        imd.SetDimensions(mim.GetDimensions())
        imd.SetSpacing(mim.GetSpacing())
        imd.SetOrigin(mim.GetOrigin())

        # if mim.GetScalarTypeMin()>=0: #unsigned
        #   mim.SetScalarType(mim.GetScalarType()-1)
        # imd.SetScalarType(mim.GetScalarType())

        IJK=vtk.vtkMatrix4x4()
        master.GetIJKToRASMatrix(IJK)
        merge.SetIJKToRASMatrix(IJK)

        nd=slicer.vtkMRMLScalarVolumeDisplayNode()
        slicer.mrmlScene.AddNode(nd)

        merge.AddAndObserveDisplayNodeID(nd.GetID())
        merge.SetAndObserveImageData(imd)

      warnings = self.checkForVolumeWarnings(master,merge)
      if warnings != "":
        self.errorDialog( "Warning: %s" % warnings )
        self.outputSelector.setCurrentNode(None)

  def onApplyButton(self):
    master=self.masterSelector.currentNode()
    merge=self.outputSelector.currentNode()
    self.frame.enabled=False
    logic = EdgeDetectLogic()
    algorithm=self.algorithmSel.currentIndex
    variance=self.varianceSlider.value
    thresholdmin=self.threshSlider.minimumValue
    thresholdmax=self.threshSlider.maximumValue
    print("Run the Edge detection algorithm")
    logic.run(master,merge,algorithm,variance,thresholdmin,thresholdmax)
    applicationLogic = slicer.app.applicationLogic()
    selectionNode = applicationLogic.GetSelectionNode()
    selectionNode.SetReferenceActiveVolumeID(master.GetID())

    if algorithm==1:
      #merge.SetLabelMap(0)
      merge.GetDisplayNode().SetAndObserveColorNodeID(slicer.mrmlScene.GetNodesByClassByName('vtkMRMLColorNode','Grey').GetItemAsObject(0).GetID())
      selectionNode.SetReferenceSecondaryVolumeID(merge.GetID())
      selectionNode.SetReferenceActiveLabelVolumeID(None)
    else:
      #non so perche ma altrimenti non funziona
      merge.GetDisplayNode().SetAndObserveColorNodeID(slicer.mrmlScene.GetNodesByClassByName('vtkMRMLColorNode','Grey').GetItemAsObject(0).GetID())
      #merge.SetLabelMap(1)
      merge.GetDisplayNode().SetAndObserveColorNodeID(self.coln.GetID())
      selectionNode.SetReferenceSecondaryVolumeID(None)
      selectionNode.SetReferenceActiveLabelVolumeID(merge.GetID())
    applicationLogic.PropagateVolumeSelection(0)

    self.frame.enabled=True

#
# EdgeDetectLogic
#

class EdgeDetectLogic:
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

  def run(self,inputVolume,outputVolume,algorithm=0,variance=2,thresholdmin=0,thresholdmax=0):
    """
    Run the edge detection algorithm
    """

    self.input=inputVolume
    self.output=outputVolume
    self.algorithm=algorithm
    self.variance=variance
    self.threshold=[thresholdmin,thresholdmax]

    slicer.util.delayDisplay('Running the edge detection aglorithm')

    im=self.input.GetImageData()
    cast=vtk.vtkImageCast()
    cast.SetOutputScalarTypeToDouble()
    cast.SetInputData(im)
    cast.Update()

    em=slicer.vtkITKEdgeDetection()
    em.SetInputData(cast.GetOutput())
    em.SetAlgorithmInt(self.algorithm)
    em.Setvariance(self.variance)
    em.Setthreshold(self.threshold)
    em.Update()

    self.output.GetImageData().DeepCopy(em.GetOutput())

    return True
