

import GWApp

"""
    Here is the NPT equivalent: (or close to it)
    <td>
       <a tal:define="
basenames item/getBaseNames;
link python:len(basenames) and basenames[0].replace(' ','+') or 'index='+str(item.getIndex());
label python:str(basenames or 'unnamed')"
          href=""
          tal:attributes="href link" 
          tal:content="label">click me</a>
    </td>

"""

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

def getLink(self,label='no label',use_all_basenames=0,index_link=1):
    basenames = self.getBaseNames()
    link = 'index=' + str(self.getIndex())
    if len(basenames):
        if use_all_basenames:
            label = str(basenames)
        else:
            label = basenames[0]
        if basenames[0].find(' ') < 0 \
           and not self.app.use_indices_in_links \
           and not index_link:
            link = basenames[0]
    return """<a href="%s">%s</a>""" % (link,label)
        
GWApp.TMObject.getLink = getLink



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
