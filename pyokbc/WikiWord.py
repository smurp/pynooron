

__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: WikiWord.py,v 1.1 2003/06/28 21:47:42 smurp Exp $'

import re
import string

def make_wiki_word(input):
    words = re.findall('\w*',input)
    words = [(i) for i in words if i != ''] # remove blanks
    #print "words =",words    
    words = [(string.upper(i[0])+i[1:]) for i in words ] # initial caps
    #print "words =",words
    return string.join(words,'')
