

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

def getLink(self,label='no label',use_all_basenames=0):
    basenames = self.getBaseNames()
    link = 'index=' + str(self.getIndex())
    if len(basenames):
        if use_all_basenames:
            label = str(basenames)
        else:
            label = basenames[0]
        if basenames[0].find(' ') < 0 and not self.app.use_indices_in_links:
            link = basenames[0]
    return """<a href="%s">%s</a>""" % (link,label)
        
GWApp.TMObject.getLink = getLink


