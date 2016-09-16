import os
import unittest
import makeROIGhost
from makeROIGhost import makeROIGhostLogic
import ROIStatistics
from ROIStatistics import ROIStatisticsLogic
from __main__ import vtk, qt, ctk, slicer
import math
import QCLib
import operator
import numpy

#
# MTF
#

class MTF:
  def __init__(self, parent):
    parent.title = "MTF"
    parent.categories = ["QC"]
    parent.dependencies = []
    parent.contributors = ["Gina Belmonte(AOUS)"]
    parent.helpText = """
    Calculate Modulation Tranfer Function (MTF) for spatial resolution quality controls
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
    slicer.selfTests['MTF'] = self.runTest

  def runTest(self):
    tester = MTFTest()
    tester.runTest()

#
# qMTFWidget
#

class MTFWidget(QCLib.genericPanel):
  def __init__(self, parent = None):
    QCLib.genericPanel.__init__(self,parent)
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
    types=["Edge","Line (Not Implemented)","Point","Droedge (Not Implemented)"]
    self.typeSel.addItems(types)
    self.typeSel.editable=False
    self.typeSel.setCurrentIndex(0)
    parametersFormLayout.addRow("Type of Analysis", self.typeSel)

    # #edge algorithm selector
    # self.algorithmSel = ctk.ctkComboBox()
    # algorithms=["Canny","Sobel","Zero Crossing Based"]
    # self.algorithmSel.addItems(algorithms)
    # #self.algorithmSel.enabled=False
    # self.algorithmSel.editable=False
    # self.algorithmSel.setCurrentIndex(0)
    # parametersFormLayout.addRow("Edge Detection Algorithm", self.algorithmSel)

    # #distance transform algorithm selector
    # self.distalgorithmSel = ctk.ctkComboBox()
    # distalgorithms=["Maurer Signed","Approximate Signed","Danielsson Signed","VTK Unsigned"]
    # self.distalgorithmSel.addItems(distalgorithms)
    # self.distalgorithmSel.editable=False
    # self.distalgorithmSel.setCurrentIndex(0)
    # parametersFormLayout.addRow("Distance Transform Algorithm", self.distalgorithmSel)

    #save intermediate
    self.intermediateCB = ctk.ctkCheckBox()
    self.intermediateCB.setChecked(False)
    parametersFormLayout.addRow("Save intermediate images and curves",self.intermediateCB)

    #options
    optionsCollapsibleButton = ctk.ctkCollapsibleButton()
    optionsCollapsibleButton.text = "Options"
    self.framelayout.addWidget(optionsCollapsibleButton)

    optionsFormLayout = qt.QFormLayout(optionsCollapsibleButton)

    self.edgeoptionframe=qt.QFrame()
    self.edgeoptionframe.enabled=False
    edgeoptionFormLayout = qt.QFormLayout(self.edgeoptionframe)
    self.pointoptionframe=qt.QFrame()
    self.pointoptionframe.enabled=False
    pointoptionFormLayout = qt.QFormLayout(self.pointoptionframe)

    optionsCollapsibleButton.layout().addWidget(self.edgeoptionframe)
    optionsCollapsibleButton.layout().addWidget(self.pointoptionframe)
    
    #edge options
    
    #symmetrize LSF
    self.symmetrizeCB = ctk.ctkCheckBox()
    self.symmetrizeCB.setChecked(True)
    self.symmetrizeCB.enabled=True
    edgeoptionFormLayout.addRow("Symmetrize LSF",self.symmetrizeCB)

    #point options

    #detection point criteria
    self.pointCB = ctk.ctkCheckBox()
    self.pointCB.setChecked(True)
    self.pointCB.enabled=True
    pointoptionFormLayout.addRow("Point object BRIGHTER than background",self.pointCB)

    # self.objradSB=ctk.ctkDoubleSpinBox()
    # self.objradSB.minimum=0
    # self.objradSB.maximum=10
    # self.objradSB.value=0.5
    # pointoptionFormLayout.addRow("Radius of object point(mm)",self.objradSB)

    self.setOptions()

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    self.framelayout.addWidget(self.applyButton)

    arrayValCollapsibleButton = ctk.ctkCollapsibleButton()
    arrayValCollapsibleButton.text = "Array Value"
    self.framelayout.addWidget(arrayValCollapsibleButton)

    # Layout within the dummy collapsible button
    arrayValFormLayout = qt.QFormLayout(arrayValCollapsibleButton)

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
    self.ArraySelector.setToolTip( "Array for analysis" )
    arrayValFormLayout.addRow("Function to interpolate: ", self.ArraySelector)

    self.abscissaSB=ctk.ctkDoubleSpinBox()
    self.abscissaSB.minimum=0
    self.abscissaSB.maximum=0
    self.abscissaSB.value=0
    self.abscissaSB.enabled=False
    arrayValFormLayout.addRow("Abscissa Value: ",self.abscissaSB)

    self.ordinateVal=qt.QLineEdit()
    self.ordinateVal.readOnly=True
    self.ordinateVal.text=""
    arrayValFormLayout.addRow("Value: ",self.ordinateVal)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.masterSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.ROISelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.ArraySelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelectArray)
    self.abscissaSB.connect("valueChanged(double)",self.getOrdinate)
    self.typeSel.connect("currentIndexChanged(int)",self.setOptions)
    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.masterSelector.currentNode() and self.ROISelector.currentNode()

  def setOptions(self):
    self.edgeoptionframe.enabled=(self.typeSel.currentIndex==0)
    self.pointoptionframe.enabled=(self.typeSel.currentIndex==2)

  def onApplyButton(self):
    logic = MTFLogic()
    print("Calculate MTF")
    self.frame.enabled=False
    input=self.masterSelector.currentNode()
    ROI=self.ROISelector.currentNode()
    typeAn=self.typeSel.currentIndex
    intSave=self.intermediateCB.checked
    symmetrize=self.symmetrizeCB.checked
    pointBrill=self.pointCB.checked
    #objrad=self.objradSB.value
    edgeAlg=0
    distAlg=0
    logic.run(input,ROI,typeAn,intSave,symmetrize,pointBrill,edgeAlg,distAlg)
    self.frame.enabled=True

  def onSelectArray(self,arrayNode):
    if arrayNode:
      array=arrayNode.GetArray()
      self.ordinateVal.text=""
      l=array.GetNumberOfTuples()
      self.abscissaSB.minimum=array.GetComponent(0,0)
      self.abscissaSB.maximum=array.GetComponent(l-1,0)
      self.abscissaSB.value=max(0.5*self.abscissaSB.maximum,self.abscissaSB.minimum)
      self.abscissaSB.enabled=True
    else:
      self.ordinateVal.text=""
      self.abscissaSB.minimum=0
      self.abscissaSB.maximum=0
      self.abscissaSB.value=0
      self.abscissaSB.enabled=False

  def getOrdinate(self,abscissa):
    if self.ArraySelector.currentNode():
      array=self.ArraySelector.currentNode().GetArray()
      l=array.GetNumberOfTuples()
      x=[]
      y=[]
      for n in range(l):
        x.append(array.GetComponent(n,0))
        y.append(array.GetComponent(n,1))
      ordinate=numpy.interp([abscissa],x,y)

      self.ordinateVal.text=str(ordinate[0])

      return ordinate[0]
    else:
      self.ordinateVal.text=""
      return None

#
# MTFLogic
#

class MTFLogic:
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


  def run(self,inputVolume,ROIVolume,analysisType,intermediateSave=False,symmetrize=True,pointBrill=True,algorithm=0,distanceMapAlgorithm=0):
    """
    Calculate MTF
    """
    self.input=inputVolume
    self.ROI=ROIVolume
    self.algorithm=algorithm
    self.analysisType=analysisType
    self.distalg=distanceMapAlgorithm
    self.intermSave=intermediateSave
    self.symmetrize=symmetrize
    self.pointBrill=pointBrill
    #self.objrad=objrad

    #nbin=int(20*(distMap.GetScalarRange()[1]-distMap.GetScalarRange()[0]+1))
    nbin=512

    scale=self.input.GetSpacing()[0] #todo:adjust
    qu=QCLib.QCUtil()

    rect=qu.minRectangle(self.ROI)
    index=0
    for i in range(rect['xmin'].__len__()):
      if rect['xmin'][i]>=0:
        index=i  #slice of ROI
        break
    xmin=rect['xmin'][index]
    xmax=rect['xmax'][index]
    ymin=rect['ymin'][index]
    ymax=rect['ymax'][index]

    arraysuffix=self.input.GetName()+"-"+self.ROI.GetName()+"-array"

    arrays=[[],[]]
    intermarrays=[[],[]]

    if self.analysisType==0: #edge
      edgeImg=vtk.vtkImageData()
      signDistImg=vtk.vtkImageData() #sign of distance map
      self.detectEdgeInROI(edgeImg,signDistImg) #detect edge in ROI and create a sign map for distance

      distMap=self.GetDistanceMap(edgeImg,signDistImg)

      if self.intermSave:
        edge=vtk.vtkImageData()
        edge.DeepCopy(self.ROI.GetImageData())
        for x in range(xmin,xmax+1):
          for y in range(ymin,ymax+1):
            val=edgeImg.GetScalarComponentAsDouble(x,y,index,0)
            edge.SetScalarComponentFromDouble(x,y,index,0,val)

        self.saveIntermediateImage('edge',edge)

        distance=vtk.vtkImageData()
        distance.DeepCopy(self.ROI.GetImageData())
        for x in range(xmin,xmax+1):
          for y in range(ymin,ymax+1):
            val=distMap.GetScalarComponentAsDouble(x,y,index,0)
            distance.SetScalarComponentFromDouble(x,y,index,0,val)

        self.saveIntermediateImage('distanceMap',distance)

      dists=[]
      vals=[]
      for x in range(xmin,xmax+1):
        for y in range(ymin,ymax+1):
          dists.append(distMap.GetScalarComponentAsDouble(x,y,index,0)*scale)
          vals.append(self.input.GetImageData().GetScalarComponentAsDouble(x,y,index,0))
      histVals=[dists,vals]
      
      #number of bin per isodistance
      #nbin=int(20*(distMap.GetScalarRange()[1]-distMap.GetScalarRange()[0]+1))
      #nbin=512

      ESF=qu.Rebin(histVals,nbin,min(dists),max(dists),True)
      ESFsort=list(zip(*sorted(zip(*ESF),key=lambda x: x[0])))
      ESFsort=[list(ESFsort[0]),list(ESFsort[1])]

      if ESFsort[1][0]>ESF[1][len(ESFsort[1])-1]:
        ESFsort=self.mirrorCurve(ESFsort)

      LSFsort=qu.DDerive(ESFsort)

      #self.objrad=0
      if self.symmetrize:
        zeroIdx=LSFsort[0].index(0)
        halflen=min(zeroIdx,len(LSFsort[1])-zeroIdx)
        SymLSFx=[]
        SymLSFy=[]

        for n in range(-halflen+1,halflen):
          SymLSFx.append(LSFsort[0][zeroIdx+n])
          SymLSFy.append(numpy.mean([LSFsort[1][zeroIdx-n],LSFsort[1][zeroIdx+n]]))

          SymLSF=[SymLSFx,list(SymLSFy)]
        OTF=self.getOTF(SymLSF)
      else:
        OTF=self.getOTF(LSFsort)

      if self.intermSave:
        intermarrays[0].append(ESFsort)
        intermarrays[1].append("ESF-"+arraysuffix)
        intermarrays[0].append(LSFsort)
        intermarrays[1].append("LSF-"+arraysuffix)
        if self.symmetrize:
          intermarrays[0].append(SymLSF)
          intermarrays[1].append("SymLSF-"+arraysuffix)

    elif self.analysisType==2: #point
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

      if self.pointBrill: #point is the voxel with max value in ROI
        psfIndex=numpy.argmax(imROIar)
      else: #point is the voxel with min value in ROI
        psfIndex=numpy.argmin(imROIar)

      [Dx,Dy,Dz]=imROI.GetDimensions()
      y=psfIndex/Dx
      x=psfIndex-Dx*y
      psfPoint=[x+xmin,y+ymin,index]
      print(psfPoint)

      print(imROIar[0,y,x])
      if imROIar[0,y,x]<0:
        imROIar=-imROIar

      backArray=imROIar[0,:,0:4]
      background=backArray.mean()

      print(background)

      #prepare distance map
      dists=[]
      vals=[]
      for x in range(xmin,xmax+1):
        for y in range(ymin,ymax+1):
          dists.append(math.sqrt((x-psfPoint[0])**2+(y-psfPoint[1])**2)*scale)
          vals.append(imROIar[0,y-ymin,x-xmin]-background)
      histVals=[dists,vals]

      PSF=qu.Rebin(histVals,nbin,min(dists),max(dists),True)
      PSFsort=list(zip(*sorted(zip(*PSF),key=lambda x: x[0])))
      PSFsort=[list(PSFsort[0]),list(PSFsort[1])]

      PSFsym=[[],[]]

      for n in range(-len(PSFsort[0])+1,len(PSFsort[0])):
        PSFsym[0].append(math.copysign(1,n)*PSFsort[0][int(math.fabs(n))])
        PSFsym[1].append(PSFsort[1][int(math.fabs(n))])

      PSFsym=qu.Rebin(PSFsym,nbin,min(PSFsym[0]),max(PSFsym[0]),True)

      if self.intermSave:
        intermarrays[0].append(PSFsort)
        intermarrays[1].append("PSF-"+arraysuffix)
        intermarrays[0].append(PSFsym)
        intermarrays[1].append("PSFsym-"+arraysuffix)

      OTF=self.getOTF(PSFsym)

    MTFy=qu.modulus(OTF[1])

    MTF=[OTF[0],MTFy]

    MTFresamp=qu.Rebin(MTF,nbin,0,self.freqSamp,True)
    MTFy=qu.normalize(MTFresamp[1])
    MTFr=[MTFresamp[0],MTFy]

    arrays[0].append(MTFr)
    arrays[1].append("MTF-"+arraysuffix)

    self.createCurves(arrays,intermarrays)

    [chartNode,SFchartNode]=self.prepareCharts()

    for n in range(len(arrays[0])):
      arrayNode=slicer.mrmlScene.GetNodesByClassByName("vtkMRMLDoubleArrayNode",arrays[1][n]).GetItemAsObject(0)
      chartNode.AddArray(arrays[1][n], arrayNode.GetID())

      if self.intermSave:
        for n in range(len(intermarrays[0])):
          arrayNode=slicer.mrmlScene.GetNodesByClassByName("vtkMRMLDoubleArrayNode",intermarrays[1][n]).GetItemAsObject(0)
          SFchartNode.AddArray(intermarrays[1][n], arrayNode.GetID())

    return True

  def mirrorCurve(self,hist):
    X=hist[0]
    Y=hist[1]

    Xmirror=[]
    Ymirror=[]

    for n in range(len(X)-1,-1,-1):
      Xmirror.append(-X[n])
      Ymirror.append(Y[n])

    return [Xmirror,Ymirror]
      

  def createCurves(self,arrays,intermarrays=[[],[]]):
    for n in range(len(arrays[0])):
      self.CreateAndFillArray(arrays[0][n],arrays[1][n])
    if self.intermSave:
      for n in range(len(intermarrays[0])):
        self.CreateAndFillArray(intermarrays[0][n],intermarrays[1][n])
    

  #Chart
  def prepareCharts(self):
    layoutNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
    layoutNodes.SetReferenceCount(layoutNodes.GetReferenceCount()-1)
    layoutNodes.InitTraversal()
    layoutNode = layoutNodes.GetNextItemAsObject()
    layoutNode.SetViewArrangement(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpQuantitativeView)

    chartViewNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
    chartViewNodes.SetReferenceCount(chartViewNodes.GetReferenceCount()-1)
    chartViewNodes.InitTraversal()
    chartViewNode = chartViewNodes.GetNextItemAsObject()

    chartNode = slicer.mrmlScene.GetNodesByClassByName("vtkMRMLChartNode","OTF").GetItemAsObject(0)
    if not chartNode:
      chartNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
      chartNode.SetName("OTF")

      print("set properties")

      chartNode.SetProperty('default', 'title', 'OTF')
      chartNode.SetProperty('default', 'xAxisLabel', 'lp/mm')
      chartNode.SetProperty('default', 'yAxisLabel', 'Signal')
      chartNode.SetProperty('default', 'type', 'Line')
      chartNode.SetProperty('default', 'showLegend', 'on')
      chartNode.SetProperty('default', 'Markers', 'on')

    chartViewNode.SetChartNodeID(chartNode.GetID())

    SFchartNode = None
    if self.intermSave:
      SFchartNode = slicer.mrmlScene.GetNodesByClassByName("vtkMRMLChartNode","SF").GetItemAsObject(0)
      if not SFchartNode:
        SFchartNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
        SFchartNode.SetName("SF")

        print("set properties")

        SFchartNode.SetProperty('default', 'title', 'SF')
        SFchartNode.SetProperty('default', 'xAxisLabel', 'mm')
        SFchartNode.SetProperty('default', 'yAxisLabel', 'Signal')
        SFchartNode.SetProperty('default', 'type', 'Line')
        SFchartNode.SetProperty('default', 'showLegend', 'on')
        SFchartNode.SetProperty('default', 'Markers', 'on')

    return [chartNode,SFchartNode]


  #intermediate images
  def saveIntermediateImage(self,name,image):
    node=slicer.mrmlScene.GetNodesByClassByName('vtkMRMLScalarVolumeNode',name).GetItemAsObject(0)

    if not node:
      node=slicer.vtkMRMLScalarVolumeNode()

      IJK=vtk.vtkMatrix4x4()
      self.input.GetIJKToRASMatrix(IJK)
      node.SetName(name)
      node.SetIJKToRASMatrix(IJK)
      #node.SetLabelMap(1)
      slicer.mrmlScene.AddNode(node)

    node.SetAndObserveImageData(image)

  def getOTF(self,SF):
      fftSF=numpy.fft.rfft(SF[1])
      step=SF[0][1]-SF[0][0]
      halfN=int((len(fftSF)+1)/2)
      freqMax=(0.5/step)*((2*halfN-3.0)/(2.0*halfN))
      #self.freqSamp=2.0/self.input.GetSpacing()[0]
      self.freqSamp=1/self.input.GetSpacing()[0]
      freqStep=0.5/(step*halfN)
      MTFLen=int((freqMax+1)/freqStep)
      freq=list(numpy.linspace(0,freqMax,MTFLen))

      ReOTF=[[],[]]
      ImOTF=[[],[]]

      ReOTF[0]=freq
      ImOTF[0]=freq
      ReOTF[1]=numpy.real(fftSF[0:len(freq)])
      ImOTF[1]=numpy.imag(fftSF[0:len(freq)])

      #if self.objrad>0:
        # for n in range(len(freq)):
        #   if freq[n]>0:
        #     OSF=math.sin(freq[n]*self.objrad)/(freq[n]*self.objrad)
        #   else:
        #     OSF=1
        #   ReOTF[1][n]=ReOTF[1][n]/OSF
        #   ImOTF[1][n]=ImOTF[1][n]/OSF

      OTF=[freq,[ReOTF[1],ImOTF[1]]]

      return OTF

  def CreateAndFillArray(self,hist,name):
    arrayNode = slicer.mrmlScene.GetNodesByClassByName("vtkMRMLDoubleArrayNode",name).GetItemAsObject(0)

    if not arrayNode:
      arrayNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
      arrayNode.SetName(name)

    arrayD = arrayNode.GetArray()

    arrayD.SetNumberOfTuples(len(hist[0]))

    for n in range(len(hist[0])):
      arrayD.SetComponent(n, 0, hist[0][n])
      arrayD.SetComponent(n, 1, hist[1][n])

    return arrayNode

  #edge: image to store the edge
  #alternateEdge: image to store the sign of distance (+1: inside, -1: outside)
  def detectEdgeInROI(self,edge,alternateEdge=None):
    qu=QCLib.QCUtil()

    VOIROI=qu.getVOIfromRectROI(self.ROI)

    eV=vtk.vtkExtractVOI()
    
    eV.SetInputData(self.input.GetImageData())
    eV.SetVOI(VOIROI)
    eV.Update()
    
    imROI=eV.GetOutput()

    thr=[0,0]
    if self.algorithm==0:
      #find threshold for edge detection
      mL=makeROIGhostLogic()
      ghost=vtk.vtkImageData()
      ghnode=slicer.vtkMRMLScalarVolumeNode()
      ghnode.SetAndObserveImageData(ghost)
      mL.run(self.input,ghnode)

      rL=ROIStatisticsLogic()
      rL.run(self.input,ghnode)
      zROI=VOIROI[4]
      ghVals=[]
      stats=rL.stats.values()
      for n in range(rL.stats.__len__()):
        ghVals.append(stats[n][zROI]['mean']+stats[n][zROI]['sd'])
      thr=[max(ghVals),2*max(ghVals)]
    else:
      alternateEdge=None

    cast=vtk.vtkImageCast()
    cast.SetOutputScalarTypeToDouble()
    cast.SetInputData(imROI)
    cast.Update()

    em=slicer.vtkITKEdgeDetection()
    em.SetInputData(cast.GetOutput())
    em.SetAlgorithmInt(self.algorithm)
    em.Setthreshold(thr)
    em.Setvariance(5)
    em.Update()

    edge.DeepCopy(em.GetOutput())

    if alternateEdge:
      self.signedDistance(edge,alternateEdge)

  #2D map of sign of distance
  #the upperleft corner (not edge) is positive
  def signedDistance(self,edgeImg,altedgeImg):
    altedgeImg.DeepCopy(edgeImg)

    qu=QCLib.QCUtil()

    VOIROI=qu.getVOIfromRectROI(self.ROI)

    #the upperleft voxel is not in edge
    if edgeImg.GetScalarComponentAsDouble(VOIROI[0],VOIROI[2],VOIROI[4],0)==0:
      altedgeImg.SetScalarComponentFromDouble(VOIROI[0],VOIROI[2],VOIROI[4],0,1)
      findedge=False
      val=0
      for x in range(VOIROI[0]+1,VOIROI[1]+1):
        if edgeImg.GetScalarComponentAsDouble(x,VOIROI[2],VOIROI[4],0)==0:
          if not findedge:
            val=1
          else:
            val=-1
        else:
          if val!=0:
            findedge=not findedge
          val=0
        altedgeImg.SetScalarComponentFromDouble(x,VOIROI[2],VOIROI[4],0,val)

      findedge=False
      for y in range(VOIROI[2]+1,VOIROI[3]+1):
        if edgeImg.GetScalarComponentAsDouble(VOIROI[0],y,VOIROI[4],0)==0:
          if not findedge:
            val=1
          else:
            val=-1
        else:
          if val!=0:
            findedge=not findedge
          val=0
        altedgeImg.SetScalarComponentFromDouble(VOIROI[0],y,VOIROI[4],0,val)

      #check for rows the side of voxel
      for y in range(VOIROI[2]+1,VOIROI[3]+1):
        findedge=False
        capo=altedgeImg.GetScalarComponentAsDouble(VOIROI[0],y,VOIROI[4],0)
        for x in range(VOIROI[0]+1,VOIROI[1]+1):
          if edgeImg.GetScalarComponentAsDouble(x,y,VOIROI[4],0)==0:
            if not findedge:
              val=capo
            else:
              val=-capo
          else:
            if val!=0:
              findedge=not findedge
            val=0
          altedgeImg.SetScalarComponentFromDouble(x,y,VOIROI[4],0,val)
    #if the upper left corner in the edge find the first voxel not in edge
    #check for rows and then column
    else:
      findNoEdge=False
      for y in range(VOIROI[2],VOIROI[3]+1):
        for x in range(VOIROI[0]+1,VOIROI[1]+1):
          if edgeImg.GetScalarComponentAsDouble(x,y,VOIROI[4],0)!=0:
            findNoEdge=True
            xF=x
            yF=y
            break
          else:
            altedgeImg.SetScalarComponentFromDouble(x,y,VOIROI[4],0,0)
        if findNoEdge:
          break

      if not findNoEdge:
        print("Error wrong ROI")
        return -1
      else:
        altedgeImg.SetScalarComponentFromDouble(xF,yF,VOIROI[4],0,1)

        findedge=False
        for x in range(xF+1,VOIROI[1]+1):
          if edgeImg.GetScalarComponentAsDouble(x,yF,VOIROI[4],0)==0:
            if not findedge:
              val=1
            else:
              val=-1
          else:
            if val!=0:
              findedge=not findedge
            val=0
          altedgeImg.SetScalarComponentFromDouble(x,yF,VOIROI[4],0,val)

        findedge=False
        for y in range(yF+1,VOIROI[3]+1):
          if edgeImg.GetScalarComponentAsDouble(xF,y,VOIROI[4],0)==0:
            if not findedge:
              val=1
            else:
              val=-1
          else:
            if val!=0:
              findedge=not findedge
            val=0
          altedgeImg.SetScalarComponentFromDouble(xF,y,VOIROI[4],0,val)

        #check for rows the side of voxel
        for y in range(yF+1,VOIROI[3]+1):
          findedge=False
          capo=altedgeImg.GetScalarComponentAsDouble(VOIROI[0],y,VOIROI[4],0)
          for x in range(xF+1,VOIROI[1]+1):
            if edgeImg.GetScalarComponentAsDouble(x,y,VOIROI[4],0)==0:
              if not findedge:
                val=capo
              else:
                val=-capo
            else:
              if val!=0:
                findedge=not findedge
              val=0
            altedgeImg.SetScalarComponentFromDouble(x,y,VOIROI[4],0,val)

          findedge=False
          capo=altedgeImg.GetScalarComponentAsDouble(VOIROI[0],y,VOIROI[4],0)
          for x in range(0,xF-1):
            if edgeImg.GetScalarComponentAsDouble(x,y,VOIROI[4],0)==0:
              if not findedge:
                val=capo
              else:
                val=-capo
            else:
              if val!=0:
                findedge=not findedge
              val=0
            altedgeImg.SetScalarComponentFromDouble(x,y,VOIROI[4],0,val)

  def GetDistanceMap(self,edgeImg,altedgeImg):
    tmpimage=vtk.vtkImageData()
    
    cast=vtk.vtkImageCast()
    cast.SetOutputScalarTypeToDouble()
    cast.SetInputData(edgeImg)
    cast.Update()

    #invert edge image edge=0 and background=2x
    Math=vtk.vtkImageMathematics()
    Math.SetInput1Data(cast.GetOutput())
    Math.SetConstantC(0)
    Math.SetConstantK(2)
    Math.SetOperationToReplaceCByK()
    Math.Update()
    tmpimage.DeepCopy(Math.GetOutput())

    Math.SetInput1Data(tmpimage)
    Math.SetConstantC(1)
    Math.SetConstantK(0)
    Math.Update()
    cast.SetInputData(Math.GetOutput())
    cast.Update()
    tmpimage.DeepCopy(cast.GetOutput())

    tmpimage2=vtk.vtkImageData()

    #calculate distance map
    if self.distalg==0:
      dm=slicer.vtkITKSignedDistanceTransform()
      # tmpimage.SetSpacing(self.input.GetSpacing())
      # dm.SetUseImageSpacing(True)
      dm.SetAlgorithmToSignedMaurer()
      dm.SetInputData(tmpimage)
      dm.Update()
      tmpimage2.DeepCopy(dm.GetOutput())
    elif self.distalg==1:
      dm=slicer.vtkITKSignedDistanceTransform()
      dm.SetAlgorithmToApproximateSigned()
      dm.SetInputData(tmpimage)
      dm.Update()
      tmpimage2.DeepCopy(dm.GetOutput())
    elif self.distalg==2:
      dm=slicer.vtkITKSignedDistanceTransform()
      # tmpimage.SetSpacing(self.input.GetSpacing())
      # dm.SetUseImageSpacing(True)
      dm.SetAlgorithmToSignedDanielsson()
      dm.SetObjectValue(2)
      dm.SetInputData(tmpimage)
      dm.Update()
      tmpimage2.DeepCopy(dm.GetOutput())
    elif self.distalg==3:
      dm=vtk.vtkImageEuclideanDistance()
      #tmpimage.SetSpacing(self.input.GetSpacing())
      dm.InitializeOn()
      #dm.ConsiderAnisotropyOn()
      dm.SetInputData(tmpimage)
      dm.Update()
      Math.SetInputData(dm.GetOutput())
      Math.SetOperationToSquareRoot()
      Math.Update()
      tmpimage2.DeepCopy(Math.GetOutput())

    if not altedgeImg:
      altedgeImg=tmpimage2

    qu=QCLib.QCUtil()
    rect=qu.minRectangle(self.ROI)
    for i in range(rect['xmin'].__len__()):
      if rect['xmin'][i]>=0:
        index=i
        break
    xmin=rect['xmin'][index]
    xmax=rect['xmax'][index]
    ymin=rect['ymin'][index]
    ymax=rect['ymax'][index]

    distMap=vtk.vtkImageData()
    distMap.DeepCopy(edgeImg)
    for x in range(xmin,xmax+1):
      for y in range(ymin,ymax+1):
        isedge=math.copysign(edgeImg.GetScalarComponentAsDouble(x,y,index,0)-1,1)
        if self.distalg!=3:
          val=math.copysign((math.fabs(tmpimage2.GetScalarComponentAsDouble(x,y,index,0))+1)*isedge,altedgeImg.GetScalarComponentAsDouble(x,y,index,0))
        else:
          val=math.copysign((math.fabs(tmpimage2.GetScalarComponentAsDouble(x,y,index,0)))*isedge,altedgeImg.GetScalarComponentAsDouble(x,y,index,0))
        distMap.SetScalarComponentFromDouble(x,y,index,0,val)

    return distMap
