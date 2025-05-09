#  Copyright (c) 2010 Franz Allan Valencia See
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from Ldap3Library.connection_manager import Ldap3ConnectionManager
from Ldap3Library.query import Ldap3Query
from Ldap3Library.version import VERSION

__version__ = VERSION

class Ldap3Library(Ldap3ConnectionManager, Ldap3Query):
    """Ldap3Library is a [https://robotframework.org|Robot Framework] library for LDAP operations using [https://github.com/cannatag/ldap3/|ldap3].

    This library provides keywords to interact with LDAP servers, including
    connecting, searching, modifying entries, and more.

    == Table of Contents ==
    %TOC%
    = Requirements =
    - Python
    - Robot Framework
    - ldap3
    - ldif
    - assertionengine

    = Installtion =
    | `pip install robotframework-ldap3`

    = Basic Usage =
    Ldap3Library leverages URL formated LDAP connection information as one gets from [https://directory.apache.org/studio/|Apache Directory Studio] or [https://ldapvi.sourceforge.net/|ldapvi]. 
    The URL format is as follows:
    | <ldap/ldaps>://<host>:<port>/<base_dn>?<attributes>?<scope>?<filter>
    For existing searches in Apache Directory Studio, you can copy the URL from the context menu in the "LDAP Browser" view.
    [ADS_ContextMenu|./resources/img/ApDiSt_AdvSe.png]


    | *** Settings ***
    | Library    Ldap3Library
    | Suite Setup    Connect to LDAP Server
    | Suite Teardown    Disconnect  ldap://localhost:389/cn=admin,dc=example,dc=com???(objectClass=*) 
    |
    | *** Variables ***
    | 
    |
    | *** Keywords ***
    | Connect to LDAP Server
    |     # Optional: Use a certificate for secure connection
    |     Connect    
    |     ...  ldap_url=ldap://localhost:389/cn=admin,dc=example,dc=com???(objectClass=*)
    |     ...  bind_dn=cn=admin,dc=example,dc=com
    |     ...  password=password
    |     ...  cert_path ${CURDIR}${/}path${/}to${/}certificate.pem
    |
    | *** Test Cases ***
    | Check Object Exists
    |     [Documentation]    Check if an object exists in the LDAP directory.
    |     [Tags]    ldap3
    |     Check Object Exists    ldap://localhost:389/cn=admin,dc=example,dc=com???(objectClass=*)

    For more detailed information please see the [./docs/connection_manager.html|Connection Manager] and [./docs/query.html|Query] documentation.
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self):
        Ldap3ConnectionManager.__init__(self)
        Ldap3Query.__init__(self)
        