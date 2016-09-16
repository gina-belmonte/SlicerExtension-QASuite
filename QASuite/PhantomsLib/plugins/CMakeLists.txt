#-----------------------------------------------------------------------------
set(MODULE_NAME PhantomsLib)
#set(MODULE_TITLE ${MODULE_NAME})

string(TOUPPER ${MODULE_NAME} MODULE_NAME_UPPER)

#-----------------------------------------------------------------------------

set(MODULE_PYTHON_SCRIPTS
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

