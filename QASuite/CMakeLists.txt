cmake_minimum_required(VERSION 2.8.9)

project(QASuite)
set(MODULE_NAME QASuite)


#-----------------------------------------------------------------------------
set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Documentation/4.3/Extensions/QASuite")
set(EXTENSION_CATEGORY "QC")
set(EXTENSION_CONTRIBUTORS "Gina Belmonte (AOUS)")
set(EXTENSION_DESCRIPTION "Suite of utilities to control quality of digital medical images")
set(EXTENSION_ICONURL "http://viewvc.slicer.org/viewvc.cgi/Slicer4/trunk/Extensions/Testing/QASuite/QASuite.png?revision=21746&view=co")
set(EXTENSION_SCREENSHOTURLS "http://wiki.slicer.org/slicerWiki/images/4/42/Slicer-r19441-QASuite-screenshot.png")

#-----------------------------------------------------------------------------
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-------------------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  )

set(MODULE_PYTHON_RESOURCES
  QASuite.png
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )

#---------------------------------------------------------------------

add_subdirectory(QCLib)
add_subdirectory(ErodeImage)
add_subdirectory(VolumeStatistics)
add_subdirectory(makeROI)
add_subdirectory(ROIStatistics)
add_subdirectory(SNR)
add_subdirectory(makeROIGhost)
add_subdirectory(GeometricDistortion)
add_subdirectory(EdgeDetect)
add_subdirectory(MTF)
add_subdirectory(SliceThk)
add_subdirectory(PhantomsLib)
add_subdirectory(LabelStatisticsExt)
add_subdirectory(CrossCorrCalculator)

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
