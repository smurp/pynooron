#!/usr/bin/python2.1

"""
TODO

* PyOkbc must support operations minimally required by Nooron:
** multiple parallel KBs (ie meta_kb)
** default values  [so there can be default values for assocated NPTs]
** value inheritance, from class to individual (template_slots)
** merging KBs (parent_kbs) for the NooronApp architecture
** refering to frames by frame_name
*** coerce_to_frame
*** coerce_to_handle

"""

from PyOkbc import *

#from OkbcPythonKb import OkbcPythonKb

#mykb = OkbcPythonKb()



#mykb = open_kb("OkbcTestData.py")
mykb = open_kb("/tmp/out.py")
goto_kb(mykb)

save_kb()
#dump_kb(mykb)
