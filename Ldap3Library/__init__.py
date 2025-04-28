from .ldap3library import Ldap3ConnectionManager
from .version import VERSION

__version__ = VERSION

class Ldap3Library(Ldap3ConnectionManager):
    """Ldap3Library is a Robot Framework library for LDAP operations using ldap3.

    This library provides keywords to interact with LDAP servers, including
    connecting, searching, modifying entries, and more.
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = VERSION

    def __init__(self):
        Ldap3ConnectionManager.__init__(self)