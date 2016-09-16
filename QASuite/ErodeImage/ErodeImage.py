import os
import unittest
import vtk
import QCLib
import slicer
from __main__ import vtk, qt, ctk, slicer

#
# ErodeImage
#

class ErodeImage:
  def __init__(self, parent):
    parent.title = "Erode Image (2D and 3D)"
    parent.categories = ["QC.Process"]
    parent.dependencies = []
    parent.contributors = ["Gina Belmonte (AOUS)"]
    parent.helpText = """
    Perform the erosion of a image
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
    slicer.selfTests['ErodeImage'] = self.runTest

  def runTest(self):
    tester = ErodeImageTest()
    tester.runTest()

#
# qErodeImageWidget
#

class ErodeImageWidget (QCLib.genericPanel):
  def __init__(self, parent = None):
    QCLib.genericPanel.__init__(self,parent)
    self.newROI=True

    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    QCLib.genericPanel.setup(self)

    #
    # ROI collapsible button
    #
    self.label = ctk.ctkCollapsibleButton(self.frame)
    self.label.setText("ROI")
    self.label.enabled=False
    self.framelayout.addWidget(self.label)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(self.label)

    #
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    # self.outputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    # self.outputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    self.outputSelector.nodeTypes = ["vtkMRMLLabelMapVolumeNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = False
    self.outputSelector.renameEnabled = True
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene(slicer.mrmlScene)
    self.outputSelector.setToolTip("ROI")
    parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

    # Radius of erosion
    self.radiusslider = ctk.ctkSliderWidget()
    self.radiusslider.singleStep = 1.0
    self.radiusslider.minimum = 0.0
    #self.radiusslider.maximum = 1.0
    self.radiusslider.value = 1.0
    self.radiusslider.enabled = False
    self.radiusslider.setToolTip("Set radius of erosion for mask creation")
    parametersFormLayout.addRow("Radius", self.radiusslider)

    # Number of erosions
    self.iterslider = ctk.ctkSliderWidget()
    self.iterslider.singleStep = 1.0
    self.iterslider.minimum = 1.0
    #self.iterslider.maximum = 1.0
    self.iterslider.value = 1.0
    self.iterslider.enabled = False
    self.iterslider.setToolTip("Set number of erosions to perform")
    parametersFormLayout.addRow("Iterations", self.iterslider)

    #Connectivity collapsible button
    self.conn = ctk.ctkCollapsibleButton(self.frame)
    self.conn.setText("Conectivity")
    self.framelayout.addWidget(self.conn)

    # Layout within the dummy collapsible button
    connFormLayout = qt.QFormLayout(self.conn)

    self.frame1=qt.QFrame(self.frame)
    self.frame1.setLayout(qt.QVBoxLayout())
    connFormLayout.addRow(self.frame1)

    self.eightNeighbors = qt.QRadioButton("Eight Neighbors (3D)", self.frame1)
    self.eightNeighbors.setToolTip("Treat diagonally adjacent voxels as neighbors.")
    self.eightNeighbors.checked = False
    self.frame1.layout().addWidget(self.eightNeighbors)
    self.fourNeighbors = qt.QRadioButton("Four Neighbors(3D)", self.frame1)
    self.fourNeighbors.setToolTip("Do not treat diagonally adjacent voxels as neighbors.")
    self.fourNeighbors.checked = False
    self.frame1.layout().addWidget(self.fourNeighbors)
    self.DD=qt.QRadioButton("Eight Neighbors (2D)")
    self.DD.setToolTip("2D connectivity treating diagonally adjacent voxels as neighbors.")
    self.DD.checked = True
    self.frame1.layout().addWidget(self.DD)

    #
    # Apply Buttonx
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Perform erosion"
    self.applyButton.enabled = False
    self.framelayout.addWidget(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.masterSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectInput)
    self.masterSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectROI)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.radiusslider.connect("valueChanged(double)",self.setRadius)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def setRadius(self):
    if self.radiusslider.value > 0:
      self.iterslider.maximum = int(self.radiusslider.maximum / self.radiusslider.value)
    else:
      self.iterslider.maximum = 1.0

  def onSelectROI(self):
    merge=self.outputSelector.currentNode()
    master=self.masterSelector.currentNode()

    if master:
      if merge:
        if not merge.GetImageData():
          self.newROI=True
          imd=vtk.vtkImageData()
          
          mim=master.GetImageData()
          imd.SetDimensions(mim.GetDimensions())
          imd.SetSpacing(mim.GetSpacing())
          imd.SetOrigin(mim.GetOrigin())
          #imd.SetScalarType(vtk.VTK_SHORT)
          imd.AllocateScalars(vtk.VTK_SHORT,1)
          
          masterIJKToRAS = vtk.vtkMatrix4x4()
          master.GetIJKToRASMatrix(masterIJKToRAS)
          merge.SetIJKToRASMatrix(masterIJKToRAS)
          
          nd=slicer.vtkMRMLScalarVolumeDisplayNode()
          slicer.mrmlScene.AddNode(nd)

          merge.AddAndObserveDisplayNodeID(nd.GetID())
          merge.SetAndObserveImageData(imd)

          #workaround to display ROI in Slicer??????
          parameters={}
          parameters["InputVolume"]=merge.GetID()
          parameters["OutputVolume"]=merge.GetID()
          parameters["Type"]="Short"
          castIM=slicer.modules.castscalarvolume
          slicer.cli.run(castIM,None,parameters)
          
          
          coln=slicer.vtkMRMLColorTableNode()
          coln.SetTypeToUser()
          coln.SetNumberOfColors(2)
          coln.SetColor(0,'bg',0,0,0)
          coln.SetColor(1,'fg',1,0,0)
          coln.SetOpacity(0,0)
          coln.SetOpacity(1,1)
          slicer.mrmlScene.AddNode(coln)
          merge.GetDisplayNode().SetAndObserveColorNodeID(coln.GetID())
        else:
          self.newROI=False

        warnings = self.checkForVolumeWarnings(master,merge)
        if warnings != "":
          self.errorDialog( "Warning: %s" % warnings )
          self.outputSelector.setCurrentNode(None)
        # else:
        #     applicationLogic = slicer.app.applicationLogic()
        #     selectionNode = applicationLogic.GetSelectionNode()
        #     selectionNode.SetReferenceActiveVolumeID(master.GetID())
        #     selectionNode.SetReferenceActiveLabelVolumeID(merge.GetID())
        #     applicationLogic.PropagateVolumeSelection(0)

  def onSelectInput(self):
    master=self.masterSelector.currentNode()

    self.radiusslider.enabled = False
    self.iterslider.enabled = False
    self.label.enabled=True
    self.radiusslider.maximum=0
    if master:
      self.radiusslider.maximum = master.GetImageData().GetDimensions()[0]/2
      self.radiusslider.value=1
      self.radiusslider.enabled = True
      self.iterslider.enabled = True
      self.label.enabled=True
      self.outputSelector.setCurrentNode(None)

  def onSelect(self):
    self.applyButton.enabled = self.masterSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    logic = ErodeImageLogic()
    radius = self.radiusslider.value
    iterations = int(self.iterslider.value)
    if self.eightNeighbors.checked:
      connectivity=0
    elif self.fourNeighbors.checked:
      connectivity=1
    else:
      connectivity=2
    master=self.masterSelector.currentNode()
    merge=self.outputSelector.currentNode()
    applicationLogic = slicer.app.applicationLogic()
    selectionNode = applicationLogic.GetSelectionNode()
    selectionNode.SetReferenceActiveVolumeID(master.GetID())
    selectionNode.SetReferenceActiveLabelVolumeID(merge.GetID())
    applicationLogic.PropagateVolumeSelection(0)
    self.frame.enabled=False
    logic.run(master, merge, radius, iterations, connectivity, self.newROI)
    self.newROI=False
    self.frame.enabled=True

#
# ErodeImageLogic
#

class ErodeImageLogic:
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


  def run(self,inputVolume,ROIVolume,radius,iters,connectivity,newROI):

    #slicer.util.delayDisplay('Erode the ROI with r=' +str(radius) + " N=" + str(iters) + " time(s)")

    self.QCVol=inputVolume
    self.ROI=ROIVolume
    self.radius=int(radius)
    self.iterations=iters
    self.connectivity=connectivity
    self.newROI=newROI

    self.createROI()

    return True

  def markVolumeNodeAsModified(self,volumeNode):
    """Mark all parts of a volume node as modified so that a correct
    render is triggered.  This includes setting the modified flag on the
    point data scalars so that the GetScalarRange method will return the
    correct value, and certain operations like volume rendering will
    know to update.
    http://na-mic.org/Bug/view.php?id=3076
    This method should be called any time the image data has been changed
    via an editing operation.
    Note that this call will typically schedule a render operation to be
    performed the next time the event loop is idle.
    """
    volumeNode.GetImageData().GetPointData().GetScalars().Modified()
    volumeNode.GetImageData().Modified()
    volumeNode.Modified()

  def createROI(self):
    inputImage=self.QCVol.GetImageData()
    ROIImage=self.ROI.GetImageData()

    self.ROIfromImages(inputImage,ROIImage,self.radius,self.iterations,self.connectivity,self.newROI)

  def ROIfromImages(self,inputImage,ROIImage,radius,iterations,connectivity,newROI):
    #TODO: sistemare valori
    #col=self.ROI.GetDisplayNode().GetColorNode()
    bg=0
    fg=1

    if newROI:
      #slicer.util.delayDisplay('thresholding...')
      thresh = vtk.vtkImageThreshold()
      thresh.SetInputData(inputImage)

      lo, hi = inputImage.GetScalarRange()
      min=lo + 0.25 * (hi-lo)
      max=hi

      thresh.ThresholdBetween(min, max)
      thresh.SetInValue(fg)
      thresh.SetOutValue(bg)
      thresh.SetOutputScalarType(ROIImage.GetScalarType())
      thresh.Update()

      ROIImage.DeepCopy(thresh.GetOutput())

      try:
        self.markVolumeNodeAsModified(self.ROI)
      except:
        pass

    if radius>0:
      ImageBuffer = vtk.vtkImageData()
      ImageBuffer.DeepCopy(ROIImage)

      eroder = slicer.vtkImageErodeExt()
      eroder.SetInputData(ROIImage)
      eroder.SetOutput(ImageBuffer)

      #slicer.util.delayDisplay('create kernel')
      #eroder.SetForeground(fg)
      eroder.SetbutForeground(True)
      eroder.SetBackground(bg)
      eroder.setRadius(radius,radius,1)
      if connectivity==0:
        eroder.SetNeighborTo8()
      elif connectivity==1:
        eroder.SetNeighborTo4()
      else:
        eroder.setConnectivity2D()
      
      for f in range(1,int(ROIImage.GetScalarRange()[1]+1)):
        eroder.SetForeground(f)

        #slicer.util.delayDisplay('eroding label = ' + str(f))

        for n in range(iterations):
          #ImageBuffer.DeepCopy(ROIImage)
          eroder.Update()
          ROIImage.DeepCopy(ImageBuffer)
          
      eroder.SetOutput(None)

      #slicer.util.delayDisplay('eroding done')
