#!/usr/bin/python2.1

__version__='$Revision: 1.8 $'[11:-2]
__cvs_id__ ='$Id: CachingPipeliningProducer.py,v 1.8 2003/02/07 22:54:08 smurp Exp $'

import string
import md5
import os
import copy
import stat

import popen2
import time
import fcntl, FCNTL
import select
import signal

def execute_pipeline(input,command):
    """Return the output of a shell pipeline as a string."""
    def makeNonBlocking(fd):
        fl = fcntl.fcntl(fd, FCNTL.F_GETFL)
        try:
            fcntl.fcntl(fd, FCNTL.F_SETFL, fl | FCNTL.O_NDELAY)
        except AttributeError:
            fcntl.fcntl(fd, FCNTL.F_SETFL, fl | FCNTL.FNDELAY)

    timeout = 15
    proc = popen2.Popen3(command,1)
    # fromchild, tochild, childerr
    proc.tochild.write(input)
    proc.tochild.flush()
    proc.tochild.close()
    outfile  = proc.fromchild
    outfd    = outfile.fileno()
    errfile  = proc.childerr
    errfd    = errfile.fileno()
    makeNonBlocking(outfd)
    makeNonBlocking(errfd)
    outdata = errdata = ''
    outeof = erreof = 0
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52296
    max_time_to_live = float(timeout) # 5 seconds grace period
    if int(timeout) == 0:
        max_time_to_live = 60 
    start_time = time.time()

    while 1:
        ready = select.select([outfd,errfd],[],[],1)
        if outfd in ready[0]:
            outchunk = outfile.read()
            if outchunk == '': outeof = 1
            outdata = outdata + outchunk
        if errfd in ready[0]:
            errchunk = errfile.read()
            if errchunk == '': erreof = 1
            errdata = errdata + errchunk
        if outeof and erreof: break
        if max_time_to_live + start_time < time.time():
            break
        time.sleep(0.1)
    exit_code = proc.poll()
    if exit_code == -1:
        pid = proc.pid
        os.kill(pid,signal.SIGKILL)
    elif exit_code > 0:
        print "exit code",exit_code

    return outdata


class CachingPipeliningProducer:
    def __init__(piper,canonical_request = None):
        piper._cachedir = None
        piper._canonical_request = canonical_request
        piper._pipeline = []
        piper._cachekey = None
        piper._done = 0
        piper._file = None
        piper._data = None
        piper._content_length = None
        piper._cmds = None
    def __str__(piper):
        return string.join(map(str,piper._pipeline),'\n')
    
    out_buffer_size = 1<<16

    def prime(piper):
        """Prime the pipe by associating a data source with _file."""
        (src_prod,cmds,fullpath,cached) = piper.producer_and_commands()
        if fullpath and cached:
            f = open(fullpath,'r')
            lines = f.readlines()
            fout = string.join(lines,'')            
            f.close()
            freshness = "from-cache"
        elif src_prod:
            fout = execute_pipeline(src_prod.more(),cmds)
            freshness = "freshly-generated"
        elif cmds:
            fout = execute_pipeline('',cmds)
            freshness = "from-precursor"
        else:
            raise "ThisShouldNotHappen",fullpath

        piper._content_length = len(fout)
        piper._data = fout
        #print "fout type=%s, len=%i"%(type(fout),len(fout)),fullpath
        
        return freshness

    def more(piper):
        """Execute the whole pipeline. See composite_producer &
        file_producer"""
        #print "CacingPipeliningProducer.more()"
        if piper._done:
            return ''
        else:
            piper._done = 1
            return piper._data
##            data =  piper._file.read(piper.out_buffer_size)
##            if not data:
##                piper._file.close()
##                del piper._file
##                piper._done = 1
##                return ''
##            else:
##                return data


    def content_length(piper):
        return piper._content_length or None            
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
            mt = section.mimetype()
        return mt or 'text/plain'
    def producer_and_commands(piper):
        """Return (source,commands) where source is either a
        producer or None and commands is either None or a string
        which constitutes a unix shell pipeline which does
        the least possible work, making use of any cached values
        if they exist and caching intermediate results if the
        cachedir is specified.  If source is not None then it is
        a Medusa-style producer which is intended to be called to
        feed its output down the commands pipeline."""
        sections = copy.copy(piper._pipeline)
        source = None
        fullpath = None
        cmds = []
        flip = 0
        if flip: sections.reverse()
        pos = 0
        final_fullpath = None
        num_sections = len(sections)
        while sections:
            section = sections.pop()
            (prod,cmd,fullpath,cached) \
                    = section.producer_command_fullpath_and_cached()
            if cmd :
                cmds.append(cmd)
            if prod and not cached:
                source = prod
            if pos == 0 and fullpath:
                final_fullpath = fullpath                
                if cached:
                    return [None,None,fullpath,cached]
            if pos == num_sections and fullpath:
                pass
            pos = pos + 1
        if cmds:
            if not flip: cmds.reverse()
            commands = string.join(cmds,' | ')
        else:
            commands = None
        piper._cmds = cmds
        return [source,commands,final_fullpath,None]

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

    def do_caching(pipesection):
        return pipesection._cachedir and os.path.isdir(pipesection._cachedir)

    def producer_command_fullpath_and_cached(pipesection):
        """Returns (producer,command,fullpath) where producer is only included
        if a cached result is not available.  Command is either a command
        which transforms stdin to stdout or a command which starts a
        pipeline by catting to stdout the contents of a cached file
        if it exists.  The pipeline command will tee off a cached copy
        if cachedir is not None.  The intention is that the command
        returned by this method be combined with others in a complete
        shell pipeline.  Fullpath is not None if the file already exists."""
        if pipesection.do_caching():
            fullpath = pipesection.full_path()
            if fullpath:
                if os.path.isfile(fullpath):
                    return (None,"cat %s" % fullpath,fullpath,1)
                else:
                    return (pipesection._producer,
                            "%s | tee %s" % (pipesection._command or 'cat',
                                             fullpath),fullpath,None)
        return (pipesection._producer,pipesection._command,None,None)
        
        

if __name__ == '__main__':
   
    cp = CachingPipeliningProducer(canonical_request='path,date1,date2')
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
    print cp.producer_and_commands()


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
    The path as specified in the URL.  Might be more or less specific.
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
