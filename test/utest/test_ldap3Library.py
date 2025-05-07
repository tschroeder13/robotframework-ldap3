import pytest
from Ldap3Library import Ldap3ConnectionManager, Ldap3Query
from assertionengine import AssertionOperator

user = "cn=admin,dc=example,dc=com"
password = "P4ssW0rd!"
ldap_url = "ldap://localhost:389/ou=users,dc=example,dc=com?postalCode,telephoneNumber?sub?(postalCode=13029)"
LDAP_URL_BASE =  "ldap://localhost:389/cn=tfoster,ou=users,dc=example,dc=com?postalCode,telephoneNumber??(postalCode=13029)"
LDAP_URL_SUB =  "ldap://localhost:389/ou=users,dc=example,dc=com?postalCode,telephoneNumber?sub?(postalCode=13029)"
LDAP_URL_LEVEL =  "ldap://localhost:389/ou=users,dc=example,dc=com?postalCode,telephoneNumber?one?(postalCode=13029)"

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
        ldap_url,
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
    ldap3ConMan.connect(ldap_url=ldap_url, 
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

def test_check_attribute_multi_value(mokapi):
    """Test if attribute value comparison returns True."""
    ldap3ConMan.connect(ldap_url=ldap_url, 
                        bind_dn=user, 
                        password=password)
    ldap3Query = Ldap3Query()
    result = ldap3Query.check_attribute_value(ldap_url=ldap_url, 
                                            attribute_name="telephoneNumber",
                                            assertion_operator=AssertionOperator["contains"], 
                                            expected_value="(261)555-4472", 
                                            assertion_message="Attribute value not contains (261)555-4472.")
    assert '(261)555-4472' in result, "Attribute value comparison failed."

def test_add_attribute_value(mokapi):
    """Test if attribute value is added."""
    ldap_url = LDAP_URL_BASE
    ldap3ConMan.connect(ldap_url=ldap_url, 
                        bind_dn=user, 
                        password=password)
    ldap3Query = Ldap3Query()
    result = ldap3Query.add_attribute_value(ldap_url=ldap_url, 
                                           attribute_name="telephoneNumber", 
                                           attribute_value="555-555-5555")
    ldap3Query.check_attribute_value(ldap_url=ldap_url,
                                     attribute_name="telephoneNumber",
                                     assertion_operator=AssertionOperator["contains"], 
                                     expected_value="555-555-5555", 
                                     assertion_message="Attribute value not contains 555-555-5555.")
    assert result is True, "Attribute value not added."

def test_delete_attribute_value(mokapi):
    """Test if attribute value is added."""
    ldap_url = LDAP_URL_BASE
    ldap3ConMan.connect(ldap_url=ldap_url, 
                        bind_dn=user, 
                        password=password)
    ldap3Query = Ldap3Query()
    ldap3Query.add_attribute_value(ldap_url=ldap_url, 
                                           attribute_name="telephoneNumber", 
                                           attribute_value="555-555-5555")
    ldap3Query.check_attribute_value(ldap_url=ldap_url,
                                     attribute_name="telephoneNumber",
                                     assertion_operator=AssertionOperator["contains"], 
                                     expected_value="555-555-5555", 
                                     assertion_message="Attribute value not contains 555-555-5555.")
    ldap3Query.remove_attribute_value(ldap_url=ldap_url, 
                                      attribute_name="telephoneNumber", 
                                      attribute_value="555-555-5555")
    ldap3Query.check_attribute_value(ldap_url=ldap_url, 
                                     attribute_name="telephoneNumber",
                                     assertion_operator=AssertionOperator["not contains"], 
                                     expected_value="555-555-5555", 
                                     assertion_message="Attribute value not contains 555-555-5555.")
    assert True

def test_replace_attribute_value(mokapi):
    """Test if attribute value is replaced."""
    ldap_url = LDAP_URL_BASE
    ldap3ConMan.connect(ldap_url=ldap_url, 
                        bind_dn=user, 
                        password=password)
    ldap3Query = Ldap3Query()
    ldap3Query.add_attribute_value(ldap_url=ldap_url, 
                                           attribute_name="telephoneNumber", 
                                           attribute_value="555-555-5555")
    ldap3Query.check_attribute_value(ldap_url=ldap_url,
                                     attribute_name="telephoneNumber",
                                     assertion_operator=AssertionOperator["contains"], 
                                     expected_value="555-555-5555", 
                                     assertion_message="Attribute value not contains 555-555-5555.")
    ldap3Query.replace_attribute_value(ldap_url=ldap_url, 
                                      attribute_name="telephoneNumber", 
                                      old_value="555-555-5555", 
                                      new_value="666-666-6666")
    ldap3Query.check_attribute_value(ldap_url=ldap_url, 
                                     attribute_name="telephoneNumber",
                                     assertion_operator=AssertionOperator["contains"], 
                                     expected_value="666-666-6666", 
                                     assertion_message="Attribute value not contains 666-666-6666.")
    assert True

def test_overwrite_attribute_value(mokapi):
    """Test if attribute value is replaced."""
    ldap_url = LDAP_URL_BASE
    ldap3ConMan.connect(ldap_url=ldap_url, 
                        bind_dn=user, 
                        password=password)
    ldap3Query = Ldap3Query()
    nums = ["(261)555-4472", "+49-201-555-0123", "001-821-664-8819"]
    for num in nums:
        ldap3Query.check_attribute_value(ldap_url=ldap_url,
                                        attribute_name="telephoneNumber",
                                        assertion_operator=AssertionOperator["contains"], 
                                        expected_value=num,
                                        assertion_message=f"Attribute value not contains {num}.") 
    ldap3Query.overwrite_attribute_value(ldap_url=ldap_url, 
                                      attribute_name="telephoneNumber", 
                                      attribute_value="555-555-5555")
    ldap3Query.check_attribute_value(ldap_url=ldap_url, 
                                     attribute_name="telephoneNumber",
                                     assertion_operator=AssertionOperator["contains"], 
                                     expected_value="555-555-5555", 
                                     assertion_message="Attribute value not contains 666-666-6666.")
    for num in nums:
        ldap3Query.check_attribute_value(ldap_url=ldap_url,
                                        attribute_name="telephoneNumber",
                                        assertion_operator=AssertionOperator["not contains"], 
                                        expected_value=num,
                                        assertion_message=f"Attribute value not contains {num}.") 
    assert True


def test_add_object_from_ldif(mokapi):
    """Test if object is added from LDIF."""
    ldap3ConMan.connect(ldap_url=ldap_url, 
                        bind_dn=user, 
                        password=password)
    ldap3Query = Ldap3Query()
    result = ldap3Query.add_object_from_ldif(ldap_url=ldap_url, 
                                            ldif_file="./fake_single.ldif",
                                            object_class="inetOrgPerson")
    exist = ldap3Query.object_exists(ldap_url="ldap://localhost:389/cn=jmason,ou=users,dc=example,dc=com???(objectClass=*)")
    exist = ldap3Query.object_exists(ldap_url="ldap://localhost:389/cn=khernandez,ou=users,dc=example,dc=com???(objectClass=*)")
    assert exist, "Object not added from LDIF."


def test_delete_object(mokapi):
    """Test if object is deleted."""
    ldap3ConMan.connect(ldap_url=ldap_url, 
                        bind_dn=user, 
                        password=password)
    ldap3Query = Ldap3Query()
    result = ldap3Query.add_object_from_ldif(ldap_url=ldap_url, 
                                            ldif_file="./fake_single.ldif",
                                            object_class="inetOrgPerson")
    result = ldap3Query.delete_object(ldap_url="ldap://localhost:389/cn=jmason,ou=users,dc=example,dc=com???(objectClass=*)")
    result = ldap3Query.delete_object(ldap_url="ldap://localhost:389/cn=khernandez,ou=users,dc=example,dc=com???(objectClass=*)")
    exist = ldap3Query.object_exists(ldap_url="ldap://localhost:389/cn=jmason,ou=users,dc=example,dc=com???(objectClass=*)")
    exist = ldap3Query.object_exists(ldap_url="ldap://localhost:389/cn=khernandez,ou=users,dc=example,dc=com???(objectClass=*)")
    assert not exist, "Object not deleted."