

"""
NooronUser is the wrapper for all user functionality in Nooron.

NullUser is equivalent to Zope's ANONYMOUS.
"""


class NooronUser:
    def confirm_password(self,pw):
        return pw != ''

class NullUser(NooronUser):
    pass
