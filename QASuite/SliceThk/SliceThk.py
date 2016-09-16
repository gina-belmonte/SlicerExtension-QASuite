import os
import QCLib
import unittest
import bisect
import numpy
import math
from __main__ import vtk, qt, ctk, slicer

#
# SliceThk
#

class SliceThk:
  def __init__(self, parent):
    parent.title = "Slice Thickness"
    parent.categories = ["QC"]
    parent.dependencies = []
    parent.contributors = ["Gina Belmonte(AOUS)"]
    parent.helpText = """
    This module estimate the slice thickness by imaging a wedge or ramp
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
    slicer.selfTests['SliceThk'] = self.runTest

  def runTest(self):
    tester = SliceThkTest()
    tester.runTest()

#
# qSliceThkWidget
#

class SliceThkWidget(QCLib.genericPanel):
  def __init__(self, parent = None):
    QCLib.genericPanel.__init__(self,parent)
    self.FWHMs={}
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    QCLib.genericPanel.setup(self)

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.framelayout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

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
    self.ROISelector.showHidden = False
    self.ROISelector.showChildNodeTypes = False
    self.ROISelector.setMRMLScene( slicer.mrmlScene )
    self.ROISelector.setToolTip( "ROI for analysis" )
    parametersFormLayout.addRow("Rectangular ROI: ", self.ROISelector)

    #object type selector
    self.typeSel = ctk.ctkComboBox()
    types=["Wedge","Ramp"]
    self.typeSel.addItems(types)
    self.typeSel.editable=False
    self.typeSel.setCurrentIndex(0)
    parametersFormLayout.addRow("Type of Analysis", self.typeSel)

    self.angleSB=ctk.ctkDoubleSpinBox()
    self.angleSB.minimum=0
    self.angleSB.maximum=360
    self.angleSB.value=11.3
    self.angleSB.enabled=True
    parametersFormLayout.addRow("Angle Value: ",self.angleSB)

    #direction selector
    self.directionSel = ctk.ctkComboBox()
    directions=["x vs y","y vs x","z vs x"]#todo: add all directions
    self.directionSel.addItems(directions)
    self.directionSel.editable=False
    self.directionSel.setCurrentIndex(0)
    parametersFormLayout.addRow("Direction: ", self.directionSel)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Calculate FWHM."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    resultCollapsibleButton = ctk.ctkCollapsibleButton()
    resultCollapsibleButton.text = "Results"
    self.framelayout.addWidget(resultCollapsibleButton)

    # Layout within the dummy collapsible button
    resultFormLayout = qt.QFormLayout(resultCollapsibleButton)

    #
    # Array selector
    #
    self.ArraySelector = slicer.qMRMLNodeComboBox()
    self.ArraySelector.nodeTypes = ( ("vtkMRMLDoubleArrayNode"), "" )
    self.ArraySelector.selectNodeUponCreation = False
    self.ArraySelector.addEnabled = False
    self.ArraySelector.removeEnabled = False
    self.ArraySelector.noneEnabled = True
    self.ArraySelector.showHidden = False
    self.ArraySelector.showChildNodeTypes = False
    self.ArraySelector.setMRMLScene( slicer.mrmlScene )
    self.ArraySelector.setToolTip( "Ramp profile" )
    resultFormLayout.addRow("Ramp profile: ", self.ArraySelector)

    self.FWHMVal=qt.QLineEdit()
    self.FWHMVal.readOnly=True
    self.FWHMVal.text=""
    resultFormLayout.addRow("FWHM: ",self.FWHMVal)

    self.SliceThkVal=qt.QLineEdit()
    self.SliceThkVal.readOnly=True
    self.SliceThkVal.text=""
    resultFormLayout.addRow("SliceThk: ",self.SliceThkVal)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.masterSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.ROISelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.ArraySelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectArray)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onSelectArray(self,arrayNode):
    if arrayNode:
      try:
        self.FWHMVal.text=self.FWHMs[arrayNode.GetName()]
        scaling=math.tan(self.angleSB.value*math.pi/180)
        self.SliceThkVal.text=self.FWHMs[arrayNode.GetName()]*scaling
        return
      except:
        pass

    self.FWHMVal.text=""
    self.SliceThkVal.text=""
      
  def onSelect(self):
    self.applyButton.enabled = self.masterSelector.currentNode() and self.ROISelector.currentNode()

  def onApplyButton(self):
    logic = SliceThkLogic()
    print("Estimate slice thickness")
    self.frame.enabled=False
    logic.run(self.masterSelector.currentNode(), self.ROISelector.currentNode(),self.typeSel.currentIndex,self.directionSel.currentIndex)
    self.FWHMs[logic.arrayName]=logic.FWHM
    self.frame.enabled=True

#
# SliceThkLogic
#

class SliceThkLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    self.step=1
    self.spacing=1
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

  def run(self,inputVolume,ROIVolume,Type=0,Direction=0):
    """
    Estimate slice thickness
    """

    slicer.util.delayDisplay('Estimate slice thickness')

    self.input=inputVolume
    self.ROI=ROIVolume
    self.type=Type
    self.direction=Direction

    self.getSliceThk(True)

    return True

  def getSliceThk(self,meanProfile=False):
    profiles=self.getProfile(self.direction)
    self.spacing=self.input.GetSpacing()[self.direction] #todo: adjust

    if not meanProfile:
      profile=profiles[int(len(profiles)/2)]
      X=range(len(profile))
    else:
      [X,profile]=self.meanTprofiles(profiles)
      
    if self.type==0:
      ramp=list(numpy.diff(profile)/numpy.diff(X))
    else:
      ramp=profile

    FWHMres=self.getFWHM(ramp,X)
    self.FWHM=FWHMres[0]

    FWHMcurve=[[FWHMres[1],FWHMres[1],FWHMres[2],FWHMres[2]],[0,FWHMres[3],FWHMres[3],0]]

    layoutNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
    layoutNodes.SetReferenceCount(layoutNodes.GetReferenceCount()-1)
    layoutNodes.InitTraversal()
    layoutNode = layoutNodes.GetNextItemAsObject()
    layoutNode.SetViewArrangement(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpQuantitativeView)

    chartViewNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
    chartViewNodes.SetReferenceCount(chartViewNodes.GetReferenceCount()-1)
    chartViewNodes.InitTraversal()
    chartViewNode = chartViewNodes.GetNextItemAsObject()

    ProfileNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
    ProfileNode.SetName("Profile-"+self.input.GetName()+"-"+self.ROI.GetName()+"-array")
    self.arrayName=ProfileNode.GetName()
    Profile = ProfileNode.GetArray()

    Profile.SetNumberOfTuples(len(ramp))

    for n in range(len(ramp)):
      Profile.SetComponent(n, 0, self.spacing*X[n])
      Profile.SetComponent(n, 1, ramp[n])

    FWHMNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
    FWHMNode.SetName("FWHM-"+self.input.GetName()+"-"+self.ROI.GetName()+"-array")
    FWHMarray = FWHMNode.GetArray()

    FWHMarray.SetNumberOfTuples(len(FWHMcurve[0]))

    for n in range(len(FWHMcurve[0])):
      FWHMarray.SetComponent(n, 0, FWHMcurve[0][n])
      FWHMarray.SetComponent(n, 1, FWHMcurve[1][n])

    chartNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
    chartNode.SetName("Profile")

    chartNode.AddArray("Profile", ProfileNode.GetID())
    chartNode.AddArray("FWHM", FWHMNode.GetID())

    chartViewNode.SetChartNodeID(chartNode.GetID())

    print("set properties")

    chartNode.SetProperty('default', 'title', 'Profile')
    chartNode.SetProperty('default', 'xAxisLabel', 'Distance(mm)')
    chartNode.SetProperty('default', 'yAxisLabel', 'Profile')
    chartNode.SetProperty('default', 'type', 'Line')
    chartNode.SetProperty('default', 'showLegend', 'on')
    chartNode.SetProperty('default', 'Markers', 'on')

  def getFWHM(self,ramp,X=None):
    profileMax=max(ramp)
    profileMin=min(ramp)
    if X is None:
      X=range(len(ramp))

    if math.fabs(profileMin)<math.fabs(profileMax):
      halfMax=(profileMax-profileMin)/2.0+profileMin
    else:
      halfMax=(profileMin-profileMax)/2.0+profileMax
    l=len(ramp)

    for n in range(l-1):
      if (math.fabs(ramp[n])<=math.fabs(halfMax) and math.fabs(ramp[n+1])>=math.fabs(halfMax)):
        break

    #leftIdx=bisect.bisect_left(ramp,halfMax)
    leftIdx=n
    leftx=X[leftIdx]*self.spacing
    leftx2=X[leftIdx+1]*self.spacing

    x=[leftx,leftx2]
    y=[math.fabs(ramp[leftIdx]),math.fabs(ramp[leftIdx+1])]

    x1=numpy.interp(math.fabs(halfMax),y,x)

    for n in range(l-1):
      if (math.fabs(ramp[l-1-n])<=math.fabs(halfMax) and math.fabs(ramp[l-1-n-1])>=math.fabs(halfMax)):
        break

    rightIdx=(l-1-n)
    #rightIdx=bisect.bisect_left(ramp,halfMax,leftIdx+1)
    rightx=X[rightIdx]*self.spacing
    rightx2=X[rightIdx-1]*self.spacing

    x=[rightx,rightx2]
    y=[math.fabs(ramp[rightIdx]),math.fabs(ramp[rightIdx-1])]

    x2=numpy.interp(math.fabs(halfMax),y,x)

    FWHM=(x2-x1)

    return [FWHM,x1,x2,halfMax]

  #direction: 0->x profile vs y,1->y profile vs x,2->z profile vs x
  def getProfile(self,direction=0):
    qu=QCLib.QCUtil()

    VOIROI=qu.getVOIfromRectROI(self.ROI)

    eV=vtk.vtkExtractVOI()
    
    eV.SetInputData(self.input.GetImageData())
    eV.SetVOI(VOIROI)
    eV.Update()
    
    imROI=vtk.vtkImageData()
    imROI.DeepCopy(eV.GetOutput())
    node=slicer.vtkMRMLScalarVolumeNode()
    node.SetAndObserveImageData(imROI)
    node.SetName('tmp')
    slicer.mrmlScene.AddNode(node)
    imROIar=slicer.util.array(node.GetName())
    slicer.mrmlScene.RemoveNode(node)

    if direction<2:
      ROImeanAr=numpy.mean(imROIar,0) #mean along z axis
    else:
      ROImeanAr=numpy.mean(imROIar,1) #mean along y axis


    profile=[]
    if direction==0 or direction==2:
      #lineProfile=int(ROImeanAr.shape[0]/2) #line at half of ROI
      for line in range(ROImeanAr.shape[0]):
        profile.append(list(ROImeanAr[line,:]))
    else:
      #lineProfile=int(ROImeanAr.shape[1]/2) #line at half of ROI
      for line in range(ROImeanAr.shape[1]):
        profile.append(list(ROImeanAr[:,line]))

    return profile

  def meanTprofiles(self,profiles):
    centroid=[]
    minX=[]
    maxX=[]
    Profiles=[]
    for l in range(len(profiles)):
      profile=profiles[l]
      X=numpy.arange(len(profile))
      res=self.getFWHM(profile)
      if self.type==1: #ramp
        centroid.append((res[2]-res[1])/2+res[1])
      else: #wedge
        centroid.append(res[1])

      X=X-centroid[l]

      Profiles.append([X,profile])

      minX.append(min(X))
      maxX.append(max(X))

    minFinX=max(minX)
    maxFinX=min(maxX)
    profLen=maxFinX-minFinX
    nbin=512
    self.step=float(profLen)/nbin
    XFin=numpy.linspace(minFinX,maxFinX,nbin)

    profs=[]
    for l in range(len(profiles)):
      profs.append(list(numpy.interp(XFin,Profiles[l][0],Profiles[l][1])))

    meanProf=numpy.mean(profs,0)

    return [XFin,meanProf]
    
