#!/usr/bin/env python2.1

__version__='$Revision: 1.1 $'[11:-2]
__cvs_id__ ='$Id: test_CachingPipeliningProducer.py,v 1.1 2003/02/07 22:53:16 smurp Exp $'

import os
import sys
import string
import unittest
sys.path.append('..')
sys.path.append('../code')
from CachingPipeliningProducer import *
def str_sort(a,b):
    return cmp(str(a),str(b))


cache_path = '/tmp/nooron_cache'

canonical = "/know/somekb/someframe__dets.dot.ps.pdf\n" +\
            "kbdatestamp=1038939824\n" +\
            "nptdatestamp=1038932134\n"


class dot_producer:
    dot_eg = """digraph test123 {a -> b -> c -> a}"""
    def __init__(self):
        self._done = None
           
    def more(self):
        if self._done:
            return ''
        else:
            self._done = 1
            return self.dot_eg
           


class CacheBehaviour(unittest.TestCase):
    def __init__(self,hunh):
        unittest.TestCase.__init__(self,hunh)
        self.cp = None

    def empty_cache(self):

        cp = self.cp
        base = os.path.join(cp._cachedir,cp._cachekey)

        #proc = os.popen('ls '+base+'.*','r')
        #print "before",proc.readlines()
        #proc.close()
        #print base
        for ext in ['pdf','dot','ps']:
            path = base+'.'+ext
            try:
                os.remove(path)
            except:
                pass
                #print path
        

    def prepare_dot(self):
        cp = CachingPipeliningProducer(canonical_request=canonical)

        cp.append_pipe(PipeSection(producer=dot_producer(),
                                   extension='dot',
                                   mimetype ='application/x-graphviz'))
        
        cp.set_cachedir(cache_path)

        self.cp = cp

    def prepare_pdf(self):
        self.prepare_dot()
        cp = self.cp
        cp.append_pipe(PipeSection(command='dot -Tps ',
                                   extension='ps',
                                   mimetype = 'application/ps'))
        
        cp.append_pipe(PipeSection(command='ps2pdf - - ',
                                   extension='pdf',
                                   mimetype = 'application/pdf'))



    def test_dot(self):
        self.prepare_dot()
        self.empty_cache()

        self.assertEquals('application/x-graphviz', self.cp.mimetype())        
        prime_type = self.cp.prime()
        out = self.cp.more()
        self.assertEquals('freshly-generated',prime_type)        
        cl = self.cp.content_length()
        actual_length = len(out)
        self.assertEquals(actual_length,cl)

        # and now lets use the cached output
        self.prepare_dot()
        prime_type = self.cp.prime()
        out = self.cp.more()
        self.assertEquals('from-cache',prime_type)        


    def test_pdf(self):
        self.prepare_pdf()

        #self.empty_cache()
        # if the proceeding line is commented out then this test depends
        # on test_dot having already being run
        
        self.assertEquals('application/pdf', self.cp.mimetype())
        prime_type = self.cp.prime()
        out = self.cp.more()
        self.assertEquals('from-precursor',prime_type)
        actual_length = len(out)
        self.assertEquals(actual_length,self.cp.content_length())

        # and now lets use the cached output
        self.prepare_pdf()
        prime_type = self.cp.prime()
        out = self.cp.more() # drain it 
        self.assertEquals('from-cache',prime_type)





if __name__ == "__main__":
    unittest.main()

    print cp.mimetype()
    print cp.producer_and_commands()




hairy_dot_eg = """digraph test123 {
       a -> b -> c;
       a -> {x y};
       b [shape=box];
       c [label="hello\nworld",color=blue,fontsize=24,
            fontname="Palatino-Italic",fontcolor=red,style=filled];
       a -> z [label="hi", weight=100];
       x -> z [label="multi‐line\nlabel"];
       edge [style=dashed,color=red];
       b -> x;
       {rank=same; b x}
}
"""
