
from AuthenticatedUser import AnonymousUser

class AuthenticatedUserAuthorizer:
    """Ideally the AuthenticatedUserAuthorizer is capable of denying
    authorization in a finegrained way depending on who someone is and what
    they are entitled to as a result.  At the moment it merely authorizes
    anything so long as the user is authenticated."""
    def __init__(self,
                 message='Not authorized to perform that operation.'):
        self._message = message
        
    def denied_p(self,op):
        """Deny nothing to the authenticated."""
        if op._request.AUTHENTICATED_USER == AnonymousUser:
            return self.message
        else:
            return None
