#!/usr/bin/python2.1

__version__='$Revision: 1.5 $'[11:-2]
__cvs_id__ ='$Id: CachingPipeliningProducer.py,v 1.5 2002/12/06 20:46:17 smurp Exp $'

import string
import md5
import os
import copy


class CachingPipeliningProducer:
    def __init__(piper,canonical_request = None):
        piper._cachedir = None
        piper._canonical_request = canonical_request
        piper._pipeline = []
        piper._cachekey = None
        piper._done = 0
        piper._file = None
    def __str__(piper):
        return string.join(map(str,piper._pipeline),'\n')
    
    out_buffer_size = 1<<16
    def more(self):
        """Execute the whole pipeline. See composite_producer &
        file_producer"""
        if self._done:
            return ''
        else:
            data = self._file.read(self.out_buffer_size)
            if not data:
                self._file.close()
                del self._file
                self._done = 1
                return ''
            else:
                return data
            
    def set_canonical_request(piper,canonical_request):
        piper._canonical_request = canonical_request
        ck = piper.cachekey()
        for p in piper._pipeline:
            p.set_cachekey(ck)
    def cachekey(piper):
        """Return a key into the cache which is a hash (md5sum) of
        the canonical_request."""
        if piper._cachekey == None:
            digest = md5.new(piper._canonical_request).digest()
            piper._cachekey = '%x' * 16 % tuple(map(ord,tuple(digest)))
        return piper._cachekey
    def set_cachedir(piper,cachedir):
        piper._cachedir = cachedir
        for p in piper._pipeline:
            p.set_cachedir(cachedir)
    def append_pipe(piper,pipe):
        piper._pipeline.append(pipe)
        if piper._cachedir:
            pipe.set_cachedir(piper._cachedir)
        ck = piper.cachekey()
        if ck:
            pipe.set_cachekey(ck)
    def mimetype(piper):
        #mt = 'text/plain'
        mt = ''
        sections = copy.copy(piper._pipeline)
        #sections.reverse()
        while sections and not mt:
            section = sections.pop()
            print "========>>",section
            mt = section.mimetype()
        return mt or 'text/plain'
    def source_and_commands(piper):
        """Return (source,commands) where source is either a
        producer or None and commands is either None or a string
        which constitutes a unix shell pipeline which does
        the least possible work, making use of any cached values
        if they exist and caching intermediate results if the
        cachedir is specified.  If source is not None then it is
        a Medusa-style producer which is intended to be called to
        feed its output down the commands pipeline."""
        sections = copy.copy(piper._pipeline)
        source_p = 0
        source = None
        cmds = []
        while sections and not source_p:
            section = sections.pop()
            (src,cmd,source_p) = section.pipe_or_cached_source()
            #print "===>",src,cmd,source_p
            cmds.append(cmd)
            if src:
                source = src
        if cmds:
            cmds.reverse()
            commands = string.join(cmds,' | ')
        else:
            commands = None
        return [source,commands]

    def more(piper):
        if not piper.__dict__.get('_s_and_c'):
           piper._s_and_c = piper.source_and_commands()
        (source,commands) = piper._s_and_c
        # drain the source into the 
        if source:
           data = source.more()
           #if data:
        
class PipeSection:
    """A PipeSection is an encapsulated shell command which can be
    piped together with others and have mimetype, extension and caching
    abilities."""
    def __init__(pipesection,producer=None,command=None,
                 mimetype=None,extension=None,
                 cachedir=None,cachekey=None):
        pipesection._command = command
        pipesection._mimetype = mimetype
        pipesection._extension = extension
        pipesection._cachedir = cachedir
        pipesection._cachekey = cachekey
        pipesection._producer = producer
    def __str__(self):
        return "<PipeSection: %s %s %s >" % (
            str(self._command or self._producer),
            self._mimetype,
            self._extension)
        
    def set_cachedir(pipesection,cachedir):
        pipesection._cachedir = cachedir
    def set_cachekey(pipesection,cachekey):
        pipesection._cachekey = cachekey
    def mimetype(pipesection):
        return pipesection._mimetype
    def full_path(pipesection):
        if pipesection._cachedir and \
           pipesection._cachekey != None and \
           pipesection._extension != None:
            return os.path.join(pipesection._cachedir,
                                pipesection._cachekey + '.' +
                                pipesection._extension)
        else:
            return None
         
    def pipe_or_cached_source(pipesection):
        """Returns (command,source_p) where command is either a command
        which transforms stdin to stdout or a command which starts a
        pipeline by catting to stdout the contents of a cached file
        if it exists.  The pipeline command will tee off a cached copy
        if cachedir is not None.  The intention is that the command
        returned by this method be combined with others in a complete
        shell pipeline.  Source_p is true means that the command ignores
        stdin and hence defines the begining of a pipeline."""
        cmd_or_prod = pipesection._command or pipesection._producer
        if pipesection._cachedir and os.path.isdir(pipesection._cachedir):
            fullpath = pipesection.full_path()
            if fullpath:
                if os.path.isfile(fullpath):
                    return (None,"cat %s" % fullpath,1)
                else:
                    return (pipesection._producer,
                            "%s | tee %s" % (pipesection._command or 'cat',
                                             fullpath),0)
        return (None,cmd_or_prod,0)  #bugged?



if __name__ == '__main__':
   
    cp = CachingPipeliningProducer()
    cp.append_pipe(PipeSection(producer=None,
                               extension='dot',
                               mimetype ='application/x-graphviz'))

    cp.append_pipe(PipeSection(command='dot -Tps ',
                               extension='ps',
                               mimetype = 'application/ps'))
    
    cp.append_pipe(PipeSection(command='ps2pdf - - ',
                               extension='pdf',
                               mimetype = 'application/pdf'))

    cp.set_cachedir('/tmp/nooron_cache')
    cp.set_canonical_request(
        "/know/somekb/someframe__dets.dot.ps.pdf\n" +\
        "kbdatestamp=1038939824\n" +\
        "nptdatestamp=1038932134\n")
    print cp.mimetype()
    print cp.source_and_commands()


"""
requirements of caching system
1) save all intermediate results (they might be requested too)
2) make it easy to detect and expire old cache contents
[remember that the base request is not the same as the canonical_request]
[remember that different users might have different preferences which
 could cause the output to differ, hence the canonical_request must
 contain appropriate information to cover this]
3) function even if no cache location
   dot -Tps | ps2pdf - - 
   tee MD5.dot | dot -Tps | tee MD5.ps | ps2pdf - - | tee MD5.pdf

   CACHELOC/{MD5}.canonical_request   
   CACHELOC/{MD5}.dot
   CACHELOC/{MD5}.ps
   CACHELOC/{MD5}.pdf
   CACHELOC/{MD5}.pykb
   CACHELOC/{MD5}.tell
   CACHELOC/base_request_to_MD5
     /some/base/url knowledge-stamp garment-stamp {MD5.1}
     /some/base/url knowledge-stamp garment-stamp {MD5.2}
   throw away all those which are based on old knowledge or npts.
   (the keepers are those which are current, but use different prefs)

terms:
  actual_request
    Might be the base_request or it might be only THING or it
    might specify the garment and some encoding extensions,
    in which case a base_request must be deduced.
    THING eg /know/nooron_faq
    actual_request examples:
       /know/nooron_faq
       /know/nooron_faq__faqs.html
       /know/nooron_faq__faqs.html.gz

  object_request
    The object to publish, even if it had to be deduced.
    actual_request          -->    object_request
    --------------                 --------------
    /know/nooron_faq               /know/nooron_faq
    /know/nooron_faq/U0001         /know/nooron_faq/U0001
    /know/nooron_faq__faqs.html    /know/nooron_faq
    /know/nooron_pert__aon.dot.ps  /know/nooron_pert
       
  base_request
    The base request is the path the user could (or might) have
    visited to be explicit about which GARMENT to use.  If the
    actual_request is not a base_request (bacause it does not specify
    a garment) then some algorithm (such
    as pick the first possible garment which produces .html) is
    used to determine the base_request.  Notice that no transforming
    or encoding extensions (such as .ps, .pdf, .gz) are included.
    THING__GARMENT  eg /know/nooron_faq/faq__details.html
    
  canonical_request
    The canonical request is meant to unambiguously identify the
    state of the system in such a way that the CR will only differ if
    something has happened to either the knowledge, the logic, or
    the presentation such that any cached results may be invalid.
    Initially, the canonical_request will be consist of the following
    values on succeeding lines:
       the base_request,
       the most recent change_time of all the parent_kbs
       the most recent change_time of all involved templates
       some indication of involved user preferences

  MD5
    The md5 checksum of the canonical request is what is used as
    the on-disk standin for the canonical_request.
    eg in file and directory names such as:
       CACHELOC/{MD5}.dot
       CACHELOC/{MD5}.canonical_request       

logic
0) build canonical request
1) create MD5 of the canonical request
   (url & kb-datestamp & template-datestamp, later, more)
2) if isfile(MD5.LAST): return it
3) else: for each stage, in order if it does not exist, cache it
4) return MD5.LAST if it exists
5) else: error

"""
