
__version__='$Revision: 1.6 $'[11:-2]
__cvs_id__ ='$Id: TMObject_mixin.py,v 1.6 2002/08/14 20:47:42 smurp Exp $'

import GWApp
from VeryEasy import VeryEasy

def getNooronPageTemplate(self):
    q1 = """FROM {%d} DO 
              TRAVERSE mAMa({'#role-instance'})
              TRAVERSE aAMm({'#role-class'})
            DONE AS INDEXES""" % self.index
    result = self.app.graph.STMQLExec(q1)
    for indx in result:
        clss = self.app.TMObject(indx)
        occs = clss.getOccurrences(type='ntp_for_class_instances')
    

GWApp.TMObject.getNooronPageTemplate = getNooronPageTemplate

def getLink(self,label='no label',use_all_basenames=0,index_link=0):
    #FIXME getLink doesn't as agressively use name as it could
    basenames = self.getBaseNames()
    link = 'index=' + str(self.getIndex())
    if len(basenames):
        if use_all_basenames:
            label = str(basenames)
        else:
            label = basenames[0]
        if not self.app.use_indices_in_links \
           and not index_link:
            # FIXME should really urlquote
            link = basenames[0].replace(' ','+')
    return """<a href="%s">%s</a>""" % (link,label)
GWApp.TMObject.getLink = getLink


## wrappers for security reasons
def wrapped_getSIRs(self):
    retval = GWApp.TMObject.unwrapped_getSIRs(self)
    retval2 = []
    for sir in retval:
        retval2.append(VeryEasy(sir))
    return retval2
GWApp.TMObject.unwrapped_getSIRs = GWApp.TMObject.getSIRs
GWApp.TMObject.getSIRs = wrapped_getSIRs

def wrapped_getSCR(self):
    retval = GWApp.TMObject.unwrapped_getSCR(self)
    if retval:
        ve = VeryEasy(retval)
        return ve
    return None
GWApp.TMObject.unwrapped_getSCR = GWApp.TMObject.getSCR
GWApp.TMObject.getSCR = wrapped_getSCR

def wrapped_getOccurrenceResources(self):
    retval = GWApp.TMObject.unwrapped_getOccurrenceResources(self)
    retval2 = []
    for res in retval:
        retval2.append(VeryEasy(res))
    return retval2
GWApp.TMObject.unwrapped_getOccurrenceResources = GWApp.TMObject.getOccurrenceResources
GWApp.TMObject.getOccurrenceResources = wrapped_getOccurrenceResources


# OKBC-inspired stuff

class SLOT_TYPE:  pass
OWN = SLOT_TYPE()
TEMPLATE = SLOT_TYPE()
AUTO = SLOT_TYPE()

class SLOT_CARDINALITY: pass
ALL = SLOT_CARDINALITY()

GWApp.TMObject.get_instance_direct_types = GWApp.TMObject.getClasses

def get_slot_values(self,slot,
                  slot_type = AUTO,
                  local_only_p=0,
                  number_of_values=ALL):
    retval = []
    if slot_type != TEMPLATE:
        local_occs = self.getOccurrences(typ=slot)
    if number_of_values == ALL or \
       number_of_values > len(local_occs) or \
       not local_only_p :
        for clss in self.get_instance_direct_types():
            v = clss.get_slot_values(slot,slot_type=OWN,
                                     local_only_p=local_only_p,
                                     number_of_values=ALL)
            
    return retval

GWApp.TMObject.get_slot_values = get_slot_values
GWApp.TMObject.__allow_access_to_unprotected_subobjects__ = 1
GWApp.__allow_access_to_unprotected_subobjects__ = 1




#import GW
#GW.__allow_access_to_unprotected_subobjects__ = 1
