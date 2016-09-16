import os
import unittest
from __main__ import vtk, qt, ctk, slicer

class genericPanel:

  def __init__(self, parent=None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)

      #self.setup()
      #self.parent.show()
    else:
      self.parent = parent

    self.frame=qt.QFrame()
    self.frame.setLayout(qt.QVBoxLayout())
    self.parent.layout().addWidget(self.frame)
    self.layout = self.parent.layout()
    self.framelayout=self.frame.layout()

  def setup(self):
    if slicer.app.commandOptions().noMainWindow:
      # don't build the widget if there's no place to put it
      return

    self.volumes = ctk.ctkCollapsibleButton()
    #self.volumes.setLayout(qt.QVBoxLayout())
    self.volumes.setText("Quality control volume")
    self.framelayout.addWidget(self.volumes)

    volumeLayout=qt.QFormLayout(self.volumes)

    self.masterSelector = slicer.qMRMLNodeComboBox()
    self.masterSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    #self.masterSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.masterSelector.selectNodeUponCreation = False
    self.masterSelector.addEnabled = False
    self.masterSelector.removeEnabled = False
    self.masterSelector.noneEnabled = True
    self.masterSelector.showHidden = False
    self.masterSelector.showChildNodeTypes = False
    self.masterSelector.setMRMLScene( slicer.mrmlScene )
    self.masterSelector.setToolTip( "Pick the master structural volume to performing quality controls" )
    volumeLayout.addRow("Input Volume: ", self.masterSelector)

    # node selected
    self.masterSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.select)

  def select(self):
    pass

  def getFrame(self):
    return self.frame

  def errorDialog(self, message):
    self.dialog = qt.QErrorMessage()
    self.dialog.setWindowTitle("QASuite")
    self.dialog.showMessage(message)

  def checkForVolumeWarnings(self,master,merge):
    """Verify that volumes are compatible with label calculation
    algorithm assumptions.  Returns warning text of empty
    string if none.
    """
    warnings = ""
    if not master:
      warnings = "Missing master volume"
    if merge:
      if not master.GetImageData() or not merge.GetImageData():
        return "Missing image data"
      if master.GetImageData().GetDimensions() != merge.GetImageData().GetDimensions():
        warnings += "Volume dimensions do not match\n"
      if master.GetImageData().GetSpacing() != merge.GetImageData().GetSpacing():
        warnings += "Volume spacings do not match\n"
      if master.GetImageData().GetOrigin() != merge.GetImageData().GetOrigin():
        warnings += "Volume spacings do not match\n"
      # if merge.GetScalarType() != vtk.VTK_SHORT:
      #     warnings += "Label map must be of type Short (Use Cast Scalar Volume to fix)\n"
      # if master.GetLabelMap():
      #   if master.GetImageData().GetScalarType() != vtk.VTK_SHORT:
      #     warnings += "Label map must be of type Short (Use Cast Scalar Volume to fix)\n"
      masterIJKToRAS = vtk.vtkMatrix4x4()
      mergeIJKToRAS = vtk.vtkMatrix4x4()
      master.GetIJKToRASMatrix(masterIJKToRAS)
      merge.GetIJKToRASMatrix(mergeIJKToRAS)
      for row in range(4):
        for column in range(4):
          if masterIJKToRAS.GetElement(row,column) != mergeIJKToRAS.GetElement(row,column):
            warnings += "Volume geometry does not match (Resample to fix)\n"
            print("coor: " + str(row) + " " + str(column) + " " + str(masterIJKToRAS.GetElement(row,column)) + " " + str(mergeIJKToRAS.GetElement(row,column)))
            break
    else:
      warnings += "Missing merge volume"
    return warnings
