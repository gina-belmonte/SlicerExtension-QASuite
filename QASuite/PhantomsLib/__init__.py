import pkgutil
import os,sys
from phantom import *

#TODO: dynamic upload
from philipsMR import *

# pathPL=os.path.normpath(os.path.dirname(os.path.realpath(__file__))+"/../plugins")
# files = os.listdir(pathPL)
# moduleNames = pkgutil.iter_modules(path=[pathPL])
# for loader, mod_name, ispkg in moduleNames:
#     module="plugins."+mod_name
#     print("mod " + module)
#     #Ensure that module isn't already loaded
#     if mod_name not in sys.modules:
#         # Import module
#         loaded_mod = __import__(module, fromlist=[mod_name])

