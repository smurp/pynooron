
import string

class AuthenticatedUser:
    """AuthenticatedUser is the handle to all user details.
    If the user has authenticated themselves to Nooron, an instance
    of this class is available as request.AUTHENTICATED_USER
    as AUTHENTICATED_USER in the the Garment namespace.
    The keys for standard_details are:
      FullName
      MiddleName
      FirstName
      LastName
      DateOfBirth
    The keys for the misc_details are up to the authenticator.
    """
    def __init__(self,login_id,
                 standard_details={},
                 misc_details=None,
                 auth_class=None):
        self._login_id = login_id
        self._misc_details = misc_details
        self._standard_details = standard_details
        self._auth_class = auth_class
    def __str__(self):
        if self._login_id == None:
            return "AnonymousUser"
        elif self._standard_details.has_key('FullName') and \
                 string.strip(self._standard_details['FullName']):
            return string.strip(self._standard_details['FullName']) + \
                   " (%s)" % str(self._login_id)
        else:
            return str(self._login_id)
    def __repr__(self):
        return self.__class__.__name__+ \
               "(%s,%s,%s,%s)"%(self._login_id,
                                repr(self._standard_details),
                                repr(self._misc_details),
                                self._auth_class)

AnonymousUser = AuthenticatedUser(None,{"Fullname":'Anonymous User'},{},None)
