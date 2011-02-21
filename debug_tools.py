
"""

Usage:
  Put @timed as a decorator before methods you want to time.
  Then run your code with and environment variable TIMED containing
  a regex which matches the ClassName.MethodName of the methods you
  want to show timing for.  
  The envar TIME_QUIETLY turns off lines like:
    debug_tools.timed() will time: function.get_frame_in_kb


For example:

$ TIMED=.* python myscript.py
TIMING:    20100505121116                 /-------------------- OnSaleThisWeek.run_when_store_object_recreated()
TIMING:    20100505121116                 | /-------------------- ProductInStore.set_on_special_price_using_directive('20%')
TIMED:     20100505121116        0.04 sec | \-------------------- ProductInStore.set_on_special_price_using_directive(...) ===>  None
TIMED:     20100505121116        0.05 sec \-------------------- OnSaleThisWeek.run_when_store_object_recreated( [] ) ===>  None
TIMING:    20100505121116                 /-------------------- OnSaleThisWeek.run_when_store_object_recreated()
TIMING:    20100505121116                 | /-------------------- ProductInStore.set_on_special_price_using_directive('30%')
TIMED:     20100505121116        0.04 sec | \-------------------- ProductInStore.set_on_special_price_using_directive(...) ===>  None
TIMED:     20100505121116        0.05 sec \-------------------- OnSaleThisWeek.run_when_store_object_recreated( [] ) ===>  None

$ TIMED=.*using.* python myscript.py
TIMING:    20100505121116                 /-------------------- ProductInStore.set_on_special_price_using_directive('20%')
TIMED:     20100505121116        0.04 sec \-------------------- ProductInStore.set_on_special_price_using_directive(...) ===>  None
TIMING:    20100505121116                 /-------------------- ProductInStore.set_on_special_price_using_directive('30%')
TIMED:     20100505121116        0.04 sec \-------------------- ProductInStore.set_on_special_price_using_directive(...) ===>  None




"""

global wrapper_depth
def timed(meth):
    import os
    import re
    spec = os.environ.get('TIMED','')
    patt = re.compile(spec)
    try:
        handle = str(meth.__class__.__name__) + "."
    except:
        handle = ""
    handle += str(meth.func_name)
    if not patt.match(handle) or spec == '':
        return meth
    else:
        if not os.environ.has_key('TIME_QUIETLY'):
            print "debug_tools.timed() will time:",handle
    import time
    def wrapper(*args,**kw):
        global wrapper_depth
        def make_argument_summary(summary_args,kw):
            summary_args2 = []
            for arg in summary_args:
                if str(type(arg)).count('WSGIRequest'):
                    arg = 'request'
                try:
                    summary_args2.append(str(arg))
                except Exception,e:
                    summary_args2.append('None')
            summary_args2 = tuple(summary_args2)
            retval = str(str(summary_args2))
            if kw:
                retval = retval[:-1] + ", " \
                    + str(", ".join(["%s=%s" % pair for pair in kw.items()])) + ")"
            return retval

        if not globals().has_key('wrapper_depth'):
            wrapper_depth = -1
        #n = ''.join([str(i) for i in time.localtime()])[:-5]

        n = time.strftime("%Y%m%d%H%M%S",time.localtime())
        if args:
            thing = args[0]
            classname = thing.__class__.__name__
            methname  = meth.__name__
        else:
            thing = False
            classname = ''
            methname = ''
        before_time = time.time()
        wrapper_depth_max = 10
        wrapper_depth = wrapper_depth + 1
        pipes  = str("| " *  wrapper_depth  )
        dashes = str("-" * (wrapper_depth_max - wrapper_depth))
        dashes = str("-" * wrapper_depth_max)
        before_lines = pipes + "/" + dashes
        after_lines =  pipes + "\\" + dashes
        before = "TIMING: %17s %15s %-10s %s.%s" % (n,'',before_lines,classname,methname)
        summary_args = list(args)
        argument_summary = make_argument_summary(summary_args,kw)
        print before + argument_summary
        #raise ValueError('yikes')
        retval = meth(*args,**kw)
        wrapper_depth = wrapper_depth - 1
        after_time = time.time()
        elapsed = "%*.*f sec" % (10,2,after_time - before_time)
        after  = "TIMED:  %17s %15s %-10s %s.%s" % (n,elapsed,after_lines,classname,methname)

        if 1:
            if type(retval) == dict and len(retval) > 5:
                retval_summary = "dict() with keys: " + str(retval.keys())
            elif str(type(retval)).count('HttpResponse'):
                retval_summary = str(type(retval))
            else:
                try:
                    retval_summary = str(retval)
                except Exception,e:
                    if str(e).count('NoneType'):
                        retval_summary = 'None'
                    else:
                        raise

        if len(summary_args):
            #self = summary_args.pop(0)
            pass
        else:
            self = None
        print after + argument_summary, " ===> ",retval_summary
        return retval
    return wrapper

