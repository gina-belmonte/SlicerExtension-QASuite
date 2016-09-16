#import PhantomsLib
import numpy
from ErodeImage import *
from phantom import *

class phMRbase:
    def __init__(self,parent=None):
        self.matrix=512
        self.slices=31
        self.slicethk=3
        self.FOV=240

        #SE profile [different sequence?]
        self.profile=numpy.array([[0,0.813595],
                      [1,0.813096],
                      [2,0.704632],
                      [3,0.674462],
                      [4,0.642705],
                      [5,0.736241],
                      [6,0.77184],
                      [7,0.797746],
                      [8,0.819562],
                      [9,0.832654],
                      [10,0.907242],
                      [11,0.940737],
                      [12,0.940772],
                      [13,0.940801],
                      [14,0.94075],
                      [15,0.940768],
                      [16,0.940874],
                      [17,0.926938],
                      [18,0.856329],
                      [19,0.669035],
                      [20,0.00195582],
                      [21,0.00145366],
                      [22,0],
                      [23,0.000394945],
                      [24,0],
                      [25,0],
                      [26,0.8177],
                      [27,0.857571],
                      [28,0.825466],
                      [29,0.36647],
                      [30,0.85817]])

        self.inserts={}
        self.inserts["resolution"]=[0,1]
        self.inserts["sliceThk"]=[5,10]
        self.inserts["uniform"]=[12,17]
        self.inserts["dgp"]=[20,24]

#axial acquired philips phantom
class philipsMR(phantom):
    #obtain profile ratio
    def setup(self,phImg):
        phantom.setup(self,phImg)

        self.phBase=phMRbase()

        #prepare ROI
        logic=ErodeImageLogic()
        connectivity=2
        newROI=True
        iterations=1
        #radius=5 for matrix=512x512
        radius=round(5*(float(self.matrix)/float(self.phBase.matrix))) #pixelsize?
        ROI=vtk.vtkImageData()
        logic.ROIfromImages(self.phantom, ROI, radius, iterations, connectivity, newROI)

        qu=QCLib.QCUtil()
        self.firstVolStats=qu.getVolImStatistics(self.phantom,qu.getImageMin(self.phantom))
        self.secondVolStats=qu.getVolImStatistics(ROI,1)

        self.profile=[]
        for n in range(len(self.secondVolStats.keys())-1):
            self.profile.append(float(self.secondVolStats.values()[n])/float(self.firstVolStats.values()[n]))

        self.findInserts()

    def findInserts(self):
        #interpolate to the base phantom slice thickness
        #X=numpy.linspace(0,self.phBase.slicethk*(self.slices*self.slicethk/self.phBase.slicethk),(self.slices*self.slicethk)/self.phBase.slicethk+1)
        X=numpy.arange(0,self.slices*self.slicethk,self.phBase.slicethk)
        Xp=numpy.linspace(0,(self.slices-1)*self.slicethk,self.slices)

        profileResc=numpy.interp(X,Xp,self.profile)
        profileRescMirror=numpy.fliplr([profileResc,numpy.zeros(len(profileResc))])[0,:]

        #find order of acquisition
        fwdcor=numpy.correlate(self.phBase.profile[:,1],profileResc,'full')
        rwdcor=numpy.correlate(self.phBase.profile[:,1],profileRescMirror,'full')

        reverse=False
        if numpy.amax(fwdcor)>=numpy.amax(rwdcor):
            shift=numpy.argmax(fwdcor)
        else:
            reverse=True
            shift=numpy.argmax(rwdcor)

        #align profile and base profile
        #get index of slices
        Xcor=(X/self.phBase.slicethk)-len(X)+1+shift

        #find phantom slice nearest to base inserts
        Inserts=["resolution","sliceThk","uniform","dgp"]
        for insert in Inserts:
            if (Xcor==self.phBase.inserts[insert][0]).any() or (Xcor==self.phBase.inserts[insert][1]).any():
                f=max(self.phBase.inserts[insert][0],Xcor[0])
                s=min(self.phBase.inserts[insert][1],Xcor[len(Xcor)-1])
                self.inserts[insert]=numpy.round(((numpy.array([f,s])+len(X)-1-shift)*float(self.phBase.slicethk))/float(self.slicethk))
                if reverse:
                    self.inserts[insert]=numpy.abs(self.inserts[insert]-self.slices+1)
                    (self.inserts[insert]).sort()
        

    def analyzeInsert(self,insert):
        pass
