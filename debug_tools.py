
"""

At the moment we just decorate methods with @timed to time them.

Methods so decorated are wrapped with a method which when results in
a TIMING line being produced when the method is called and a TIMED line
appearing when it returns along with the number of seconds and the return value.
The line art "/---" is meant to show the nestedness of the calls.

TIMING:    20100505121116                 /-------------------- OnSaleThisWeek.run_when_store_object_recreated
TIMING:    20100505121116                 |/------------------- ProductInStore.set_on_special_price_using_directive
TIMED:     20100505121116        0.04 sec |\------------------- ProductInStore.set_on_special_price_using_directive( ["<type 'str'>"] ) ===>  None
TIMED:     20100505121116        0.05 sec \-------------------- OnSaleThisWeek.run_when_store_object_recreated( [] ) ===>  None


Possible improvements to the formatting include:
  - show the actual parameters using proper python positional and named formatting
  - show self as the python object id (or repr?)
  - have more control over the summarizing of the return value (because sometimes they are obnoxiously long)

Maybe it should look like this:

TIMING:    20100505121116                 /-------------------- OnSaleThisWeek.run_when_store_object_recreated()
TIMING:    20100505121116                 | /-------------------- ProductInStore.set_on_special_price_using_directive('20%')
TIMED:     20100505121116        0.04 sec | \-------------------- ProductInStore.set_on_special_price_using_directive(...) ===>  None
TIMED:     20100505121116        0.05 sec \-------------------- OnSaleThisWeek.run_when_store_object_recreated( [] ) ===>  None
TIMING:    20100505121116                 /-------------------- OnSaleThisWeek.run_when_store_object_recreated()
TIMING:    20100505121116                 | /-------------------- ProductInStore.set_on_special_price_using_directive('30%')
TIMED:     20100505121116        0.04 sec | \-------------------- ProductInStore.set_on_special_price_using_directive(...) ===>  None
TIMED:     20100505121116        0.05 sec \-------------------- OnSaleThisWeek.run_when_store_object_recreated( [] ) ===>  None


In the future we want a way to easily turn this stuff on with great precision.
With features such as:
  - named patterns (called 'Timing Groups') of classes and methods to perform 'timing' on
  - the ability to set which Timing Group to use during a "./manage.py runserver" execution:
      DO_TIMING_ON=PaymentSystem ./manage.py runserver mbest
  - the ability to control how to summarize the parameters and return values from methods
  - the timing groups would be defined in a file __timing_conf__.py with contents like:

timing_groups = {
 'EveryThing':              {'matches': ['*.*'],                        # every method on every class
                             'skip'   : ['*.__getattribute__']},        # except __getattribute__()
 'CheckOut':                {'matches': ['CheckOut*.*']},               # every class starting with 'CheckOut'
 'call_to_generate_a_view': {'matches': ['*.call_to_generate_a_view']}, # ctgav on every class
 'Wizard':                  {'matches': ['Wizard.*',                    # all methods on Wizard
                                         'WizardStep.*'                 # and WizardStep
                                         ]},
}


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
        print "will time:",handle
    import time
    def wrapper(*args,**kw):
        global wrapper_depth
        def make_argument_summary():
            summary_args2 = []
            for arg in summary_args:
                if str(type(arg)).count('WSGIRequest'):
                    arg = 'request'
                summary_args2.append(str(arg))
            summary_args2 = tuple(summary_args2)

            return str(str(summary_args2))

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
        wrapper_depth_max = 20
        wrapper_depth = wrapper_depth + 1
        pipes  = str("| " *  wrapper_depth  )
        dashes = str("-" * (wrapper_depth_max - wrapper_depth))
        dashes = str("-" * wrapper_depth_max)
        before_lines = pipes + "/" + dashes
        after_lines =  pipes + "\\" + dashes
        before = "TIMING: %17s %15s %-20s %s.%s" % (n,'',before_lines,classname,methname)
        summary_args = list(args)
        argument_summary = make_argument_summary()
        print before + argument_summary
        #raise ValueError('yikes')
        retval = meth(*args,**kw)
        wrapper_depth = wrapper_depth - 1
        after_time = time.time()
        elapsed = "%*.*f sec" % (10,2,after_time - before_time)
        after  = "TIMED:  %17s %15s %-20s %s.%s" % (n,elapsed,after_lines,classname,methname)

        if 1:
            if type(retval) == dict and len(retval) > 5:
                retval_summary = "dict() with keys: " + str(retval.keys())
            elif str(type(retval)).count('HttpResponse'):
                retval_summary = str(type(retval))
            else:
                retval_summary = str(retval)

        if len(summary_args):
            #self = summary_args.pop(0)
            pass
        else:
            self = None
        print after + argument_summary, " ===> ",retval_summary
        return retval
    return wrapper

