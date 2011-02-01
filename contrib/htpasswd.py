#!/usr/bin/python
"""Replacement for htpasswd"""
# Original author: Eli Carter
# authenticate added by Shawn Murphy <smurp@smurp.com>

import os
import sys
import random
from optparse import OptionParser

# We need a crypt module, but Windows doesn't have one by default.  Try to find
# one, and tell the user if we can't.
try:
    import crypt
except ImportError:
    try:
        import fcrypt as crypt
    except ImportError:
        sys.stderr.write("Cannot find a crypt module.  "
                         "Possibly http://carey.geek.nz/code/python-fcrypt/\n")
        sys.exit(1)


def salt():
    """Returns a string of 2 randome letters"""
    letters = 'abcdefghijklmnopqrstuvwxyz' \
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
              '0123456789/.'
    return random.choice(letters) + random.choice(letters)


class HtpasswdFile:
    """A class for manipulating htpasswd files."""

    def __init__(self, filename, create=False):
        self.entries = []
        self.filename = filename
        if not create:
            if os.path.exists(self.filename):
                self.load()
            else:
                raise Exception("%s does not exist" % self.filename)

    def load(self):
        """Read the htpasswd file into memory."""
        lines = open(self.filename, 'r').readlines()
        self.entries = []
        for line in lines:
            username, pwhash = line.split(':')
            entry = [username, pwhash.rstrip()]
            self.entries.append(entry)

    def save(self):
        """Write the htpasswd file to disk"""
        open(self.filename, 'w').writelines(["%s:%s\n" % (entry[0], entry[1])
                                             for entry in self.entries])

    def update(self, username, password):
        """Replace the entry for the given user, or add it if new."""
        pwhash = crypt.crypt(password, salt())
        matching_entries = [entry for entry in self.entries
                            if entry[0] == username]
        if matching_entries:
            matching_entries[0][1] = pwhash
        else:
            self.entries.append([username, pwhash])

    def delete(self, username):
        """Remove the entry for the given user."""
        self.entries = [entry for entry in self.entries
                        if entry[0] != username]

    def authenticate(self, username, password):
        for entry in self.entries:
            if entry[0] == username:
                salt = entry[1][:2]
                if crypt.crypt(password,salt) == entry[1]:
                    return True
                else:
                    return False # ie password incorrect
        return None # ie username not present

def main():
    """%prog [-c] -b filename username password
    Create or update an htpasswd file"""
    # For now, we only care about the use cases that affect tests/functional.py
    parser = OptionParser(usage=main.__doc__)
    parser.add_option('-b', action='store_true', dest='batch', default=False,
        help='Batch mode; password is passed on the command line IN THE CLEAR.'
        )
    parser.add_option('-c', action='store_true', dest='create', default=False,
        help='Create a new htpasswd file, overwriting any existing file.')
    parser.add_option('-D', action='store_true', dest='delete_user',
        default=False, help='Remove the given user from the password file.')
    parser.add_option('-a', action='store_true', dest='authenticate',
        default=False, help='Confirm that the username:password combo is present.')

    options, args = parser.parse_args()

    def syntax_error(msg):
        """Utility function for displaying fatal error messages with usage
        help.
        """
        sys.stderr.write("Syntax error: " + msg)
        sys.stderr.write(parser.get_usage())
        sys.exit(1)


    if not options.batch:
        required_number_of_arguments = 1
    else:
        required_number_of_arguments = 2

    # Non-option arguments
    if len(args) < required_number_of_arguments:
        syntax_error("Insufficient number of arguments.\n")
    filename, username = args[:2]
    if options.delete_user:
        if len(args) != required_number_of_arguments:
            syntax_error("Incorrect number of arguments.\n")
        password = None
    else:
        if len(args) != required_number_of_arguments + 1:
            syntax_error("Incorrect number of arguments.\n")
        if options.batch:
            password = args[2]
        else:
            password = raw_input('password: ')

    passwdfile = HtpasswdFile(filename, create=options.create)

    if options.delete_user:
        passwdfile.delete(username)
    elif options.authenticate:
        resp = passwdfile.authenticate(username, password)
        if resp:
            print "Authenticated"
        elif resp == None:
            print "User %s not present" % username
        else:
            print "Wrong password"
        
    else:
        passwdfile.update(username, password)

    passwdfile.save()


if __name__ == '__main__':
    main()
