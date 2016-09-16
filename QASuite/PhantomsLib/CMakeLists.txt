#-----------------------------------------------------------------------------
set(MODULE_NAME PhantomsLib)
#set(MODULE_TITLE ${MODULE_NAME})

string(TOUPPER ${MODULE_NAME} MODULE_NAME_UPPER)

#add_subdirectory(Logic)
#add_subdirectory(Widgets)
#add_subdirectory(plugins)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  __init__.py
  phantom.py
  philipsMR.py
)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_RESOURCES
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_SUBDIR
  #WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)
  add_subdirectory(Testing)
endif()
