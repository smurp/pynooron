import re

class IPListAuthorizer:
    """IPListAuthorizer allows or denies listed IPs or allows everybody
    by default.

    usage:
      # allow only listed IPs deny everybody else
      IPListSecurityEngine(allow=['1.1.1.17'],deny=1)
      
      # deny listed IPs, allow everybody else
      IPListSecurityEngine(deny=['1.1.1.17'],allow=1)
      
      # deny everybody, tell them why
      IPListSecurityEngine(deny=1,message="On hiatus!")

    see tests/test_security.py
    """
    def __init__(self,allow=[],deny=[],
                 message='Not authorized to perform that operation.',
                 chain = None):
        self._allow   = allow
        self._deny    = deny
        self._message = message
        self._chain   = chain
        
        rule_re = '.*'
        if type(allow) == type([]):
            rule_re = string.join(allow,'|')
            if not rule_re:
                rule_re = "DENYALL"
            rule_re = string.replace(rule_re,'.','\.')
            rule_re = string.replace(rule_re,'*','\d+')
        self._rule_re = rule_re
        self._allow_re = re.compile(rule_re)
        
    def denied_p(self,op):
        addr = op._request.channel.addr[0]
        #print ">'%s'<" % addr, self._allow
        #if self._allow == 1 or addr in self._allow:
        the_guy_is_bad = type(self._deny) == type([]) and addr in self._deny
        the_guy_is_good = type(self._allow) == type([]) \
                          and self._allow_re.search(addr) != None

        #the_guy_is_good = type(self._allow) == type([]) and self._allow_re and addr in self._allow
        if the_guy_is_bad:
            return self._message
        if the_guy_is_good:
            return None
        
        if self._allow == 1:
            return None
        if self._deny == 1:
            return self._message
        
        if self._chain:
            return self._chain.denied_p(op)
        
        return self._message  # deny ALL by default
