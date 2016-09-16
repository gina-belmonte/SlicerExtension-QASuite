import os
import unittest
import time
from __main__ import vtk, qt, ctk, slicer
from makeROI import *

#
# makeROIGhost
#

class makeROIGhost:
  def __init__(self, parent):
    parent.title = "Make ROI for ghost analysis"
    parent.categories = ["QC.Process"]
    parent.dependencies = []
    parent.contributors = ["Gina Belmonte(AOUS)"]
    parent.helpText = """
    Create a ROI for ghosting analysis
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
    slicer.selfTests['makeROIGhost'] = self.runTest

  def runTest(self):
    tester = makeROIGhostTest()
    tester.runTest()

#
# qmakeROIGhostWidget
#

class makeROIGhostWidget(makeROIWidget):
  def __init__(self, parent = None):
    makeROIWidget.__init__(self,parent)

    self.suffixMergeName="-Ghostlabel"

    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    makeROIWidget.setup(self)

    self.applyButton.toolTip = "Create a ROI for Ghost Analysis"

    #self.label.hide()

    ch=self.label.children()
    for n in range(ch.__len__()-1,0,-1):
      self.label.layout().removeWidget(ch[n])
      ch[n].delete()
    self.framelayout.removeWidget(self.label)
    self.label.delete()

  def onSelectMaster(self):
    self.master = self.masterSelector.currentNode()
    merge=None

    #-----mergeVolume()
    if self.master:
      masterName = self.master.GetName()
      mergeName = masterName+self.suffixMergeName

      # if we already have a merge and the master hasn't changed, use it
      if self.merge and self.master == self.masterWhenMergeWasSet:
        mergeNode = slicer.mrmlScene.GetNodeByID(self.merge.GetID())
        if mergeNode and mergeNode !="":
          merge=self.merge

      if not merge:
        self.masterWhenMergeWasSemasterWhenMergeWasSet = None

        # otherwise pick the merge based on the master name
        # - either return the merge volume or empty string
        merge = self.getNodeByName(mergeName)
        self.merge=merge
        #-----

      if merge:
        if merge.GetClassName() != "vtkMRMLLabelMapVolumeNode":
          self.errorDialog("Error: selected merge label volume is not a label volume " + merge.GetClassName())
        else:
          warnings = self.checkForVolumeWarnings(self.master,self.merge)
          if warnings != "":
            self.errorDialog( "Warning: %s" % warnings )
          else:
            # make the source node the active background, and the label node the active label
            applicationLogic = slicer.app.applicationLogic()
            selectionNode = applicationLogic.GetSelectionNode()
            selectionNode.SetReferenceActiveVolumeID(self.master.GetID())
            selectionNode.SetReferenceActiveLabelVolumeID(merge.GetID())
            applicationLogic.PropagateVolumeSelection(0)
            self.merge = merge
      else:
        # the master exists, but there is no merge volume yet
        volumesLogic = slicer.modules.volumes.logic()
        merge = volumesLogic.CreateAndAddLabelVolume(slicer.mrmlScene, self.master, mergeName)
        coln=slicer.vtkMRMLColorTableNode()
        coln.SetTypeToUser()
        coln.SetNumberOfColors(9)
        coln.SetColor(0,'bg',0,0,0)
        coln.SetColor(1,'n',1,0,0)
        coln.SetColor(2,'ne',0,1,0)
        coln.SetColor(3,'nw',0,0,1)
        coln.SetColor(4,'e',1,1,0)
        coln.SetColor(5,'w',1,0,1)
        coln.SetColor(6,'s',0,1,1)
        coln.SetColor(7,'se',1,1,1)
        coln.SetColor(8,'sw',1,0.5,0)
        coln.SetOpacity(0,0)
        for n in range(1,9):
          coln.SetOpacity(n,1)
        slicer.mrmlScene.AddNode(coln)
        merge.GetDisplayNode().SetAndObserveColorNodeID(coln.GetID())
        self.merge = merge
        self.masterWhenMergeWasSet = self.master
        self.onSelectMaster()

  def onApplyButton(self):
    applicationLogic = slicer.app.applicationLogic()
    selectionNode = applicationLogic.GetSelectionNode()
    selectionNode.SetReferenceActiveVolumeID(self.master.GetID())
    selectionNode.SetReferenceActiveLabelVolumeID(self.merge.GetID())
    applicationLogic.PropagateVolumeSelection(0)

    self.frame.enabled=False

    logic = makeROIGhostLogic()
    print("Create a Ghost ROI")
    logic.run(self.master,self.merge)

    self.frame.enabled=True

#
# makeROIGhostLogic
#

class makeROIGhostLogic:
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

  def run(self,inputVolume,labelVolume):
    """
    Create ROI for Ghost analysis
    """

    slicer.util.delayDisplay('Create ROI for Ghost analysis')

    self.volume=inputVolume
    self.label=labelVolume

    tstart=time.time()
    self.createROIINPLACE()
    tend=time.time()

    print("time " + str(tend-tstart))

    print("Erode ROI")
    logicEr=ErodeImageLogic()
    connectivity=3
    newROI=False
    iterations=1
    radius=5
    logicEr.run(self.volume, self.label, radius, iterations, connectivity, newROI)

    return True

  def runOUTPLACE(self,inputVolume,labelVolume):
    """
    Create ROI for Ghost analysis
    """

    slicer.util.delayDisplay('Create ROI for Ghost analysis')

    self.volume=inputVolume
    self.label=labelVolume

    tstart=time.time()
    self.createROIvtk()
    tend=time.time()

    print("time " + str(tend-tstart))
    return True

  def runPyth(self,inputVolume,labelVolume):
    """
    Create ROI for Ghost analysis
    """

    slicer.util.delayDisplay('Create ROI for Ghost analysis')

    self.volume=inputVolume
    self.label=labelVolume

    tstart=time.time()
    self.createROI()
    tend=time.time()

    print("time " + str(tend-tstart))
    return True

  def createROIINPLACE(self):
    labelim=vtk.vtkImageData()
    inputImage=self.volume.GetImageData()
    labelImage=self.label.GetImageData()

    IJKToRAS = vtk.vtkMatrix4x4()
    self.volume.GetIJKToRASMatrix(IJKToRAS)
    self.label.SetIJKToRASMatrix(IJKToRAS)

    thresh = vtk.vtkImageThreshold()
    thresh.SetInputData(inputImage)

    lo, hi = inputImage.GetScalarRange()
    minimum=lo + 0.1 * (hi-lo)
    maximum=hi

    thresh.ThresholdBetween(minimum, maximum)
    thresh.SetInValue(1)
    thresh.SetOutValue(0)
    thresh.SetOutputScalarType(vtk.VTK_SHORT)
    thresh.Update()

    node=slicer.vtkMRMLScalarVolumeNode()
    node.SetIJKToRASMatrix(IJKToRAS)
    node.SetAndObserveImageData(thresh.GetOutput())
    slicer.mrmlScene.AddNode(node)
    node.SetName('tmp')

    qu=QCLib.QCUtil()

    rect=qu.minRectangle(node)

    slicer.mrmlScene.RemoveNode(node)
    
    thresh.ThresholdBetween(hi+1, hi+1)
    thresh.Update()
    labelImage.DeepCopy(thresh.GetOutput())

    # coln.SetColor(0,'bg',0,0,0)
    # coln.SetColor(1,'n',1,0,0)
    # coln.SetColor(2,'ne',0,1,0)
    # coln.SetColor(3,'nw',0,0,1)
    # coln.SetColor(4,'e',1,1,0)
    # coln.SetColor(5,'w',1,0,1)
    # coln.SetColor(6,'s',0,1,1)
    # coln.SetColor(7,'se',1,1,1)
    # coln.SetColor(8,'sw',1,0.5,0)

    north=slicer.vtkFillVOIImageFilter()
    north.SetfillValue(1)
    north.SetInputData(labelImage)
    northeast=slicer.vtkFillVOIImageFilter()
    northeast.SetfillValue(2)
    northeast.SetInputData(labelImage)
    northwest=slicer.vtkFillVOIImageFilter()
    northwest.SetfillValue(3)
    northwest.SetInputData(labelImage)
    east=slicer.vtkFillVOIImageFilter()
    east.SetfillValue(4)
    east.SetInputData(labelImage)
    west=slicer.vtkFillVOIImageFilter()
    west.SetfillValue(5)
    west.SetInputData(labelImage)
    south=slicer.vtkFillVOIImageFilter()
    south.SetfillValue(6)
    south.SetInputData(labelImage)
    southeast=slicer.vtkFillVOIImageFilter()
    southeast.SetfillValue(7)
    southeast.SetInputData(labelImage)
    southwest=slicer.vtkFillVOIImageFilter()
    southwest.SetfillValue(8)
    southwest.SetInputData(labelImage)

    dim1=inputImage.GetDimensions()[0]
    dim2=inputImage.GetDimensions()[1]
    dim3=inputImage.GetDimensions()[2]

    for z in range(dim3):
      VOIn=[rect['xmin'].values()[z],rect['xmax'].values()[z],1,rect['ymin'].values()[z],z,z]
      VOIne=[rect['xmax'].values()[z],dim1-1,1,rect['ymin'].values()[z],z,z]
      VOInw=[1,rect['xmin'].values()[z],1,rect['ymin'].values()[z],z,z]
      VOIe=[rect['xmax'].values()[z],dim1-1,rect['ymin'].values()[z],rect['ymax'].values()[z],z,z]
      VOIw=[1,rect['xmin'].values()[z],rect['ymin'].values()[z],rect['ymax'].values()[z],z,z]
      VOIs=[rect['xmin'].values()[z],rect['xmax'].values()[z],rect['ymax'].values()[z],dim2-1,z,z]
      VOIse=[rect['xmax'].values()[z],dim1-1,rect['ymax'].values()[z],dim2-1,z,z]
      VOIsw=[1,rect['xmin'].values()[z],rect['ymax'].values()[z],dim2-1,z,z]

      north.AddVOI(VOIn)
      northeast.AddVOI(VOIne)
      northwest.AddVOI(VOInw)
      east.AddVOI(VOIe)
      west.AddVOI(VOIw)
      south.AddVOI(VOIs)
      southeast.AddVOI(VOIse)
      southwest.AddVOI(VOIsw)

    north.UpdateInputImageINPLACE(labelImage)
    northeast.UpdateInputImageINPLACE(labelImage)
    northwest.UpdateInputImageINPLACE(labelImage)
    east.UpdateInputImageINPLACE(labelImage)
    west.UpdateInputImageINPLACE(labelImage)
    south.UpdateInputImageINPLACE(labelImage)
    southeast.UpdateInputImageINPLACE(labelImage)
    southwest.UpdateInputImageINPLACE(labelImage)

  def createROIvtk(self):
    labelim=vtk.vtkImageData()
    inputImage=self.volume.GetImageData()
    labelImage=self.label.GetImageData()

    IJKToRAS = vtk.vtkMatrix4x4()
    self.volume.GetIJKToRASMatrix(IJKToRAS)
    self.label.SetIJKToRASMatrix(IJKToRAS)

    thresh = vtk.vtkImageThreshold()
    thresh.SetInputData(inputImage)

    lo, hi = inputImage.GetScalarRange()
    minimum=lo + 0.25 * (hi-lo)
    maximum=hi

    thresh.ThresholdBetween(minimum, maximum)
    thresh.SetInValue(1)
    thresh.SetOutValue(0)
    thresh.SetOutputScalarType(vtk.VTK_SHORT)
    thresh.Update()

    node=slicer.vtkMRMLScalarVolumeNode()
    node.SetIJKToRASMatrix(IJKToRAS)
    node.SetAndObserveImageData(thresh.GetOutput())
    slicer.mrmlScene.AddNode(node)
    node.SetName('tmp')

    qu=QCLib.QCUtil()

    rect=qu.minRectangle(node)

    slicer.mrmlScene.RemoveNode(node)
    
    thresh.ThresholdBetween(hi+1, hi+1)
    thresh.Update()
    labelImage.DeepCopy(thresh.GetOutput())

    # coln.SetColor(0,'bg',0,0,0)
    # coln.SetColor(1,'n',1,0,0)
    # coln.SetColor(2,'ne',0,1,0)
    # coln.SetColor(3,'nw',0,0,1)
    # coln.SetColor(4,'e',1,1,0)
    # coln.SetColor(5,'w',1,0,1)
    # coln.SetColor(6,'s',0,1,1)
    # coln.SetColor(7,'se',1,1,1)
    # coln.SetColor(8,'sw',1,0.5,0)

    north=slicer.vtkFillVOIImageFilter()
    north.SetfillValue(1)
    north.SetInputData(labelImage)
    northeast=slicer.vtkFillVOIImageFilter()
    northeast.SetfillValue(2)
    northeast.SetInputData(labelImage)
    northwest=slicer.vtkFillVOIImageFilter()
    northwest.SetfillValue(3)
    northwest.SetInputData(labelImage)
    east=slicer.vtkFillVOIImageFilter()
    east.SetfillValue(4)
    east.SetInputData(labelImage)
    west=slicer.vtkFillVOIImageFilter()
    west.SetfillValue(5)
    west.SetInputData(labelImage)
    south=slicer.vtkFillVOIImageFilter()
    south.SetfillValue(6)
    south.SetInputData(labelImage)
    southeast=slicer.vtkFillVOIImageFilter()
    southeast.SetfillValue(7)
    southeast.SetInputData(labelImage)
    southwest=slicer.vtkFillVOIImageFilter()
    southwest.SetfillValue(8)
    southwest.SetInputData(labelImage)

    dim1=inputImage.GetDimensions()[0]
    dim2=inputImage.GetDimensions()[1]
    dim3=inputImage.GetDimensions()[2]

    for z in range(dim3):
      VOIn=[rect['xmin'].values()[z],rect['xmax'].values()[z],1,rect['ymin'].values()[z],z,z]
      VOIne=[rect['xmax'].values()[z],dim1-1,1,rect['ymin'].values()[z],z,z]
      VOInw=[1,rect['xmin'].values()[z],1,rect['ymin'].values()[z],z,z]
      VOIe=[rect['xmax'].values()[z],dim1-1,rect['ymin'].values()[z],rect['ymax'].values()[z],z,z]
      VOIw=[1,rect['xmin'].values()[z],rect['ymin'].values()[z],rect['ymax'].values()[z],z,z]
      VOIs=[rect['xmin'].values()[z],rect['xmax'].values()[z],rect['ymax'].values()[z],dim2-1,z,z]
      VOIse=[rect['xmax'].values()[z],dim1-1,rect['ymax'].values()[z],dim2-1,z,z]
      VOIsw=[1,rect['xmin'].values()[z],rect['ymax'].values()[z],dim2-1,z,z]

      north.AddVOI(VOIn)
      northeast.AddVOI(VOIne)
      northwest.AddVOI(VOInw)
      east.AddVOI(VOIe)
      west.AddVOI(VOIw)
      south.AddVOI(VOIs)
      southeast.AddVOI(VOIse)
      southwest.AddVOI(VOIsw)

    north.Update()
    labelImage.DeepCopy(north.GetOutput())
    northeast.Update()
    labelImage.DeepCopy(northeast.GetOutput())
    northwest.Update()
    labelImage.DeepCopy(northwest.GetOutput())
    east.Update()
    labelImage.DeepCopy(east.GetOutput())
    west.Update()
    labelImage.DeepCopy(west.GetOutput())
    south.Update()
    labelImage.DeepCopy(south.GetOutput())
    southeast.Update()
    labelImage.DeepCopy(southeast.GetOutput())
    southwest.Update()
    labelImage.DeepCopy(southwest.GetOutput())

  def createROIslow(self):
    labelim=vtk.vtkImageData()
    inputImage=self.volume.GetImageData()
    labelImage=self.label.GetImageData()

    IJKToRAS = vtk.vtkMatrix4x4()
    self.volume.GetIJKToRASMatrix(IJKToRAS)

    thresh = vtk.vtkImageThreshold()
    thresh.SetInputData(inputImage)

    lo, hi = inputImage.GetScalarRange()
    minimum=lo + 0.25 * (hi-lo)
    maximum=hi

    thresh.ThresholdBetween(minimum, maximum)
    thresh.SetInValue(1)
    thresh.SetOutValue(0)
    thresh.SetOutputScalarType(vtk.VTK_SHORT)
    thresh.Update()

    node=slicer.vtkMRMLScalarVolumeNode()
    node.SetIJKToRASMatrix(IJKToRAS)
    node.SetAndObserveImageData(thresh.GetOutput())
    slicer.mrmlScene.AddNode(node)
    node.SetName('tmp')

    qu=QCLib.QCUtil()

    rect=qu.minRectangle(node)

    slicer.mrmlScene.RemoveNode(node)

    dim1=inputImage.GetDimensions()[0]
    dim2=inputImage.GetDimensions()[1]
    dim3=inputImage.GetDimensions()[2]

    # coln.SetColor(0,'bg',0,0,0)
    # coln.SetColor(1,'n',1,0,0)
    # coln.SetColor(2,'ne',0,1,0)
    # coln.SetColor(3,'nw',0,0,1)
    # coln.SetColor(4,'e',1,1,0)
    # coln.SetColor(5,'w',1,0,1)
    # coln.SetColor(6,'s',0,1,1)
    # coln.SetColor(7,'se',1,1,1)
    # coln.SetColor(8,'sw',1,0.5,0)

    for x in range(dim1):
      for y in range(dim2):
        for z in range(dim3):

          VOIn=[rect['xmin'].values()[z],rect['xmax'].values()[z],1,rect['ymin'].values()[z]]
          VOIne=[rect['xmax'].values()[z],dim1-1,1,rect['ymin'].values()[z]]
          VOInw=[1,rect['xmin'].values()[z],1,rect['ymin'].values()[z]]
          VOIe=[rect['xmax'].values()[z],dim1-1,rect['ymin'].values()[z],rect['ymax'].values()[z]]
          VOIw=[1,rect['xmin'].values()[z],rect['ymin'].values()[z],rect['ymax'].values()[z]]
          VOIs=[rect['xmin'].values()[z],rect['xmax'].values()[z],rect['ymax'].values()[z],dim2-1]
          VOIse=[rect['xmax'].values()[z],dim1-1,rect['ymax'].values()[z],dim2-1]
          VOIsw=[1,rect['xmin'].values()[z],rect['ymax'].values()[z],dim2-1]

          if (x>=VOIn[0] and x<=VOIn[1] and y>=VOIn[2] and y<=VOIn[3]):
            labelImage.SetScalarComponentFromDouble(x,y,z,0,1)
          elif (x>=VOIne[0] and x<=VOIne[1] and y>=VOIne[2] and y<=VOIne[3]):
            labelImage.SetScalarComponentFromDouble(x,y,z,0,2)
          elif (x>=VOInw[0] and x<=VOInw[1] and y>=VOInw[2] and y<=VOInw[3]):
            labelImage.SetScalarComponentFromDouble(x,y,z,0,3)
          elif (x>=VOIe[0] and x<=VOIe[1] and y>=VOIe[2] and y<=VOIe[3]):
            labelImage.SetScalarComponentFromDouble(x,y,z,0,4)
          elif (x>=VOIw[0] and x<=VOIw[1] and y>=VOIw[2] and y<=VOIw[3]):
            labelImage.SetScalarComponentFromDouble(x,y,z,0,5)
          elif (x>=VOIs[0] and x<=VOIs[1] and y>=VOIs[2] and y<=VOIs[3]):
            labelImage.SetScalarComponentFromDouble(x,y,z,0,6)
          elif (x>=VOIse[0] and x<=VOIse[1] and y>=VOIse[2] and y<=VOIse[3]):
            labelImage.SetScalarComponentFromDouble(x,y,z,0,7)
          elif (x>=VOIsw[0] and x<=VOIsw[1] and y>=VOIsw[2] and y<=VOIsw[3]):
            labelImage.SetScalarComponentFromDouble(x,y,z,0,8)


  def createROI(self):
    labelim=vtk.vtkImageData()
    inputImage=self.volume.GetImageData()
    labelImage=self.label.GetImageData()

    IJKToRAS = vtk.vtkMatrix4x4()
    self.volume.GetIJKToRASMatrix(IJKToRAS)

    thresh = vtk.vtkImageThreshold()
    thresh.SetInputData(inputImage)

    lo, hi = inputImage.GetScalarRange()
    minimum=lo + 0.25 * (hi-lo)
    maximum=hi

    thresh.ThresholdBetween(minimum, maximum)
    thresh.SetInValue(1)
    thresh.SetOutValue(0)
    thresh.SetOutputScalarType(vtk.VTK_SHORT)
    thresh.Update()

    node=slicer.vtkMRMLScalarVolumeNode()
    node.SetIJKToRASMatrix(IJKToRAS)
    node.SetAndObserveImageData(thresh.GetOutput())
    slicer.mrmlScene.AddNode(node)
    node.SetName('tmp')

    qu=QCLib.QCUtil()

    rect=qu.minRectangle(node)

    slicer.mrmlScene.RemoveNode(node)

    dim1=inputImage.GetDimensions()[0]
    dim2=inputImage.GetDimensions()[1]
    dim3=inputImage.GetDimensions()[2]

    # coln.SetColor(0,'bg',0,0,0)
    # coln.SetColor(1,'n',1,0,0)
    # coln.SetColor(2,'ne',0,1,0)
    # coln.SetColor(3,'nw',0,0,1)
    # coln.SetColor(4,'e',1,1,0)
    # coln.SetColor(5,'w',1,0,1)
    # coln.SetColor(6,'s',0,1,1)
    # coln.SetColor(7,'se',1,1,1)
    # coln.SetColor(8,'sw',1,0.5,0)

    VOIList=[]

    for z in range(dim3):
      
      VOIn=[rect['xmin'].values()[z],rect['xmax'].values()[z],1,rect['ymin'].values()[z],1]
      VOIne=[rect['xmax'].values()[z],dim1-1,1,rect['ymin'].values()[z],2]
      VOInw=[1,rect['xmin'].values()[z],1,rect['ymin'].values()[z],3]
      VOIe=[rect['xmax'].values()[z],dim1-1,rect['ymin'].values()[z],rect['ymax'].values()[z],4]
      VOIw=[1,rect['xmin'].values()[z],rect['ymin'].values()[z],rect['ymax'].values()[z],5]
      VOIs=[rect['xmin'].values()[z],rect['xmax'].values()[z],rect['ymax'].values()[z],dim2-1,6]
      VOIse=[rect['xmax'].values()[z],dim1-1,rect['ymax'].values()[z],dim2-1,7]
      VOIsw=[1,rect['xmin'].values()[z],rect['ymax'].values()[z],dim2-1,8]

      VOIList.append(VOIn)
      VOIList.append(VOIne)
      VOIList.append(VOInw)
      VOIList.append(VOIe)
      VOIList.append(VOIw)
      VOIList.append(VOIs)
      VOIList.append(VOIse)
      VOIList.append(VOIsw)

    for v in range(VOIList.__len__()):
      VOI=VOIList[v]
      z=v/8
      for x in range(VOI[0],VOI[1]+1):
        for y in range(VOI[2],VOI[3]+1):
          labelImage.SetScalarComponentFromDouble(x,y,z,0,VOI[4])
