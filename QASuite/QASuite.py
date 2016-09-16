import os
from __main__ import slicer
import PhantomsLib
import qt

class QASuite:
  def __init__(self, parent):
    import string
    parent.title = "QASuite"
    parent.categories = ["", "QC"]
    parent.contributors = ["Gina Belmonte (AOUS)"]
    parent.helpText = string.Template("""
    A suite for quality control of medical images.
    """)
    self.parent = parent

    self.ICON_DIR = os.path.dirname(os.path.realpath(__file__))
    #print(self.ICON_DIR)

    if slicer.mrmlScene.GetTagByClassName( "vtkMRMLScriptedModuleNode" ) != 'ScriptedModule':
      node = vtkMRMLScriptedModuleNode()
      slicer.mrmlScene.RegisterNodeClass(node)
      node.Delete()

    parent.icon = qt.QIcon("%s/QASuite.png" % self.ICON_DIR)

class QASuiteWidget:
  def __init__(self, parent=None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)

      self.setup()
      self.parent.show()
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

    #
    # Load Button
    #
    self.loadButton = qt.QPushButton("Load")
    self.loadButton.toolTip = "Load QC dicom images"
    self.loadButton.enabled = True
    self.layout.addWidget(self.loadButton)

    self.loadButton.connect('clicked(bool)', self.onLoadButton)

  def onLoadButton(self):
    #dcm=ctk.ctkDICOMBrowser()
    #detailsPopup = DICOMLib.DICOMDetailsPopup(dcm,0)
    #detailsPopup.open()
    #dcm.show()

    dw=DICOMWidget()
    dw.enter()
