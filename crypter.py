#!/usr/bin/python2.1

import sys
import crypt

if __name__ == "__main__":
    pw = sys.argv[1]
    out = crypt.crypt(pw,pw[:2])
    if len(sys.argv) > 2:
        if out == sys.argv[2]:
            print "match"
        else:
            print "no match"
    else:
        print out
    
