from PyOkbc import *
from FileSystemConnection import FileSystemConnection
from  OkbcConditions import *

import inspect
okbc_functions={}
for i in inspect.getmembers(Funcs,inspect.isfunction):
    okbc_functions[i[0]]=i[1]
del inspect
