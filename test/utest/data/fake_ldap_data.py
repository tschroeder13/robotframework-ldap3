from faker import Faker
from ldif import LDIFWriter
import random

fake = Faker()

writer = LDIFWriter(open("fake_ldap_data.ldif", "wb"))
for _ in range(10):
    fname = fake.first_name()
    lname = fake.last_name()
    flname = f"{fname[0]}{lname}".lower()
    writer.unparse(dn=f"cn={flname},ou=users,dc=example,dc=com", 
            record={
            "objectClass": ["inetOrgPerson", "organizationalPerson", "person", "top"],
            "cn": [flname], #[fake.name()],
            "sn": [lname], #[fake.last_name()],
            "givenName": [fname], #[fake.first_name()],
            "mail": [f"{flname}@acme-corp.com"], #[fake.email()],
            "telephoneNumber": [fake.phone_number()],
            "title": [fake.job()],
            "uid": [fake.user_name()],
            "userPassword": ["P4ssW0rd!"], 
            "ou": [random.choice(["Engineering", "Sales", "Marketing", "HR"])],
            "l": [fake.city()],
            "st": [fake.state()],
            "postalCode": [fake.postcode()],
            "c": [fake.country_code()]
        }
    )
