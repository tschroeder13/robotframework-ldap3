from time import sleep
import pytest
from _pytest.fixtures import SubRequest

from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, MOCK_SYNC, SUBTREE, BASE, LEVEL
from ldap3.utils.uri import parse_uri
from getpass import getpass
from typing import List
from Ldap3Library.ldap3library import Ldap3ConnectionManager

class LdapConnectionProperties:
    """ FOR UNIT TESTING PURPOSES ONLY
    Class to hold connection properties."""
    def __init__(self, alias:str=None, bind:bool=False user:str=None, password:str=None, host:str=None, port:int=0, use_ssl:bool=False, dsa_info:str=None, dsa_schema:str=None, entry_json:List[str]=None):
        self.alias = alias
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.bind = bind
        self.dsa_info = dsa_info
        self.dsa_schema = dsa_schema
        self.entry_json = entry_json

def _get_fake_ldap(user=None, password=None, host=None, port=0, use_ssl=False, dsa_info=None, dsa_schema=None, entry_json=List[str]):
    """Get a fake LDAP server for testing."""
    fake_server = Server.from_definition(
        host, dsa_info, dsa_schema, port, use_ssl)
    con = Connection(fake_server, user,
                     password, client_strategy=MOCK_SYNC)
    for entry in entry_json:
        con.strategy.entries_from_json(entry)
    return con

# @pytest.fixture(scope="module")
# def ldap3Robot():
#     ldap3Robot = Ldap3Robot()
#     yield ldap3Robot

@pytest.fixture(scope="module")
def ldap3ConMan(request):
    l3r = Ldap3ConnectionManager()
    """Fixture to add a connection to the LDAP pool."""
    if (hasattr(request, "param")
        and isinstance(request.param, LdapConnectionProperties) 
        and request.param.host not in l3r.LDAP_POOL.keys()):
        conProps = request.param
        con = _get_fake_ldap(
            user=conProps.user,
            password=conProps.password,
            host=conProps.host,
            port=conProps.port,
            use_ssl=conProps.use_ssl,
            dsa_info=conProps.dsa_info,
            dsa_schema=conProps.dsa_schema,
            entry_json=conProps.entry_json
        )
        if conProps.bind:
            con.bind()
        l3r.connection_pool.register_connection(conProps.alias, con)


