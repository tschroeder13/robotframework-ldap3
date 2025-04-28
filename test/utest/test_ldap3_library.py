from Ldap3Library import Ldap3ConnectionManager
from .conftest import LdapConnectionProperties

import pytest

idvProps = LdapConnectionProperties(alias="fake1"
                                    user="cn=admin,ou=sa,o=system",
                                    password="P4ssW0rd!", 
                                    host="fake.server.local",
                                    port=666, 
                                    use_ssl=True,
                                    bind = True
                                    dsa_info="test/utest/data/idv_info.confid.txt",
                                    dsa_schema="test/utest/data/idv_schema.confid.txt",
                                    entry_json=["test/utest/data/idv_orgtree.confid.json",
                                                "test/utest/data/admin.confid.json",
                                                "test/utest/data/Identity.confid.json",
                                                "test/utest/data/tempIdent.confid.json",
                                                "test/utest/data/AD-Accts.confid.json"]
)

idvProps1 = LdapConnectionProperties(alias="fake1"
                                    user="cn=admin,ou=sa,o=system",
                                    password="P4ssW0rd!", 
                                    host="fake.server.local",
                                    port=667, 
                                    use_ssl=True,
                                    dsa_info="test/utest/data/idv_info.confid.txt",
                                    dsa_schema="test/utest/data/idv_schema.confid.txt",
                                    entry_json=["test/utest/data/idv_orgtree.confid.json",
                                                "test/utest/data/admin.confid.json",
                                                "test/utest/data/Identity.confid.json",
                                                "test/utest/data/tempIdent.confid.json",
                                                "test/utest/data/AD-Accts.confid.json"]
)

ldap_url = "ldaps://fake.server.local:666/o=data???"
bind_dn = "cn=admin,ou=sa,o=system"
password = "P4ssW0rd!"


@pytest.mark.parametrize("ldap3ConMan", [idvProps, idvProps1], indirect=True)
def test_is_connection_closed(ldap3ConMan):
    """Testif connection is closed."""
    ldap3ConMan.connect(alias="fake1", ldap_url=ldap_url, bind_dn=bind_dn, password=password)
    assert not ldap3ConMan.is_connection_closed("fake")
    assert ldap3ConMan.is_connection_closed("fake1")

