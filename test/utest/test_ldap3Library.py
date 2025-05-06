import pytest
from Ldap3Library import Ldap3ConnectionManager, Ldap3Query
from assertionengine import AssertionOperator

user = "cn=admin,dc=example,dc=com"
password = "P4ssW0rd!"
ldap_url = "ldap://localhost:389/ou=users,dc=example,dc=com?postalCode?sub?(postalCode=13029)"

ldap3ConMan = Ldap3ConnectionManager()

def test_connect(mokapi):
    """Test if connection is established."""
    ldap3ConMan.connect(ldap_url=ldap_url, 
                        bind_dn=user, 
                        password=password)
    assert not ldap3ConMan.is_connection_closed()

def test_disconnect(mokapi):
    """Test if connection is closed."""
    ldap3ConMan.connect(ldap_url=ldap_url, 
                        bind_dn=user, 
                        password=password)
    assert not ldap3ConMan.is_connection_closed()
    ldap3ConMan.disconnect(ldap_url=ldap_url)
    with pytest.raises(ValueError) as excinfo:
        ldap3ConMan.is_connection_closed()
        assert str(excinfo.value) == "No connections registered. Please register a connection first."

def test_disconnect_all(mokapi):
    """Test if all connections are closed."""
    ldap_urls = [
        "ldap://localhost:389/ou=users,dc=example,dc=com?postalCode?sub?(postalCode=13029)",
        "ldap://localhost:389/ou=users,dc=example,dc=com?postalCode?one?(postalCode=13029)"
    ]

    for _url in ldap_urls:
        ldap3ConMan.connect(ldap_url=_url, 
                            bind_dn=user, 
                            password=password)
        assert not ldap3ConMan.is_connection_closed()
    ldap3ConMan.disconnect_all()
    with pytest.raises(ValueError) as excinfo:
        ldap3ConMan.is_connection_closed()
        assert str(excinfo.value) == "No connections registered. Please register a connection first."

def test_search(mokapi):
    """Test if search returns results."""
    ldap3ConMan.connect(ldap_url="ldap://localhost:389/ou=users,dc=example,dc=com?postalCode?sub?(postalCode=13029)", 
                        bind_dn=user, 
                        password=password)
    ldap3Query = Ldap3Query()
    result = ldap3Query.search(ldap_url=ldap_url)
    assert len(result) > 0, "Search returned no results."

# def test_compare_attribute(mokapi):
#     """Test if compare_attribute returns True."""
#     _url = "ldap://localhost:389/cn=uia12345,ou=identities,ou=ident,ou=data,o=base?mobile??(objectClass=*)"
#     ldap3ConMan.connect(ldap_url=_url, 
#                         bind_dn=user, 
#                         password=password)
#     ldap3Query = Ldap3Query(ldap3ConMan)
#     result = ldap3Query.compare_attribute(ldap_url=_url, value="+99-888-777-666")
#     assert result is True, "Attribute comparison failed."


def test_object_exists(mokapi):
    """Test if object exists."""
    ldap_url = "ldap://localhost:389/cn=tfoster,ou=users,dc=example,dc=com?postalCode??(postalCode=13029)"
    ldap3ConMan.connect(ldap_url=ldap_url, 
                        bind_dn=user, 
                        password=password)
    ldap3Query = Ldap3Query()
    result = ldap3Query.object_exists(ldap_url=ldap_url)
    assert result is True, "Object does not exist."

def test_check_object_count(mokapi):
    """Test if object count matches expected."""
    ldap_url = "ldap://localhost:389/cn=tfoster,ou=users,dc=example,dc=com?postalCode??(postalCode=13029)"
    ldap3ConMan.connect(ldap_url=ldap_url, 
                        bind_dn=user, 
                        password=password)
    ldap3Query = Ldap3Query()
    result = ldap3Query.check_object_count(ldap_url=ldap_url, 
                                           assertion_operator=AssertionOperator[">="], 
                                           expected_count=1, 
                                           assertion_message="Object count mismatch.")
    assert result is True, "Object count does not match expected."

@pytest.mark.parametrize("assertion_operator, expected_value",[
                          (AssertionOperator["<="], "13030"),
                          (AssertionOperator["!="], "13028"),
                          (AssertionOperator[">"], "13028"),
                          (AssertionOperator["<"], "13030"),
                          (AssertionOperator[">="], "13028"),
                          (AssertionOperator["=="], "13029")
                          ])
def test_check_attribute_value(mokapi, assertion_operator, expected_value):
    """Test if attribute value comparison returns True."""
    ldap3ConMan.connect(ldap_url=ldap_url, 
                        bind_dn=user, 
                        password=password)
    ldap3Query = Ldap3Query()
    result = ldap3Query.check_attribute_value(ldap_url=ldap_url, 
                                            attribute_name="postalCode",
                                            assertion_operator=assertion_operator, 
                                            expected_value=expected_value, 
                                            assertion_message=f"Attribute value not {assertion_operator.value} {expected_value} .")
    assert result == '13029', "Attribute value comparison failed."