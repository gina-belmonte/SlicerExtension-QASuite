class phantom:
    def __init__(self,parent=None):
        self.inserts={}

    def setup(self,phImg):
        self.phantom=phImg

        self.matrix=self.phantom.GetDimensions()[0] #fix
        self.slices=self.phantom.GetDimensions()[2]
        self.slicethk=self.phantom.GetSpacing()[2]
        self.FOV=self.matrix*self.phantom.GetSpacing()[0]

    def findInserts(self):
        pass

    def analyzeInsert(self,insert):
        pass
