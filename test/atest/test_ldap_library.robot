*** Settings ***
Library    Ldap3Library  
Library    Process
Suite Setup    Set up
Suite Teardown    Clean up

*** Variables ***
${MOKAPI_PATH}=  D:${/}idmHelpers${/}PortableApps${/}mokapi_v0.15.0_windows_amd64${/}mokapi.exe
${PROV_FILE}=  D:${/}git_workspace${/}robotframework-ldap3${/}test${/}mocks${/}ldap.yaml
${LDAP_URL_BASE}=  ldap://localhost:389/cn=tfoster,ou=users,dc=example,dc=com?postalCode,telephoneNumber,title??(postalCode=13029)
${LDAP_URL_SUB}=  ldap://localhost:389/ou=users,dc=example,dc=com?postalCode,telephoneNumber,title?sub?(postalCode=13029)
${LDAP_URL_LEVEL}=  ldap://localhost:389/ou=users,dc=example,dc=com?postalCode,telephoneNumber,title?one?(postalCode=13029)
${LDAP_URL_SUB_MANY}=  ldap://localhost:389/ou=users,dc=example,dc=com?postalCode,telephoneNumber,title?sub?(postalCode=13029)
${LDAP_URL}=  ${LDAP_URL_BASE}
${BIND_DN}=  cn=admin,dc=example,dc=com
${PASSWORD}=  P4ssW0rd!
${CERT}=  n/a
${mokapi}=  None

*** Test Cases ***
Search LDAP with subtree scope
    ${result}=  Search    ${LDAP_URL_SUB}
    Log To Console   ${result}

Search LDAP with base scope
    ${result}=  Search    ${LDAP_URL_BASE}
    Log To Console   ${result}

Search LDAP with one level scope
    ${result}=  Search    ${LDAP_URL_LEVEL}
    Log To Console   ${result}

Search LDAP with subtree scope and return JSON
    ${result}=  Search    ${LDAP_URL_SUB}  json
    Log To Console   ${result}

Check OBject Exists
    Check Object Exists    ${LDAP_URL_BASE}
    Run Keyword And Expect Error  ValueError: Scope must be BASE*
    ...   Check Object Exists    ${LDAP_URL_SUB}
    # Run Keyword And Expect Error  STARTS:ValueError
    # ...   Check Object Exists    ldap://localhost:389/cn=notexisting,ou=users,dc=example,dc=com?postalCode,telephoneNumber,title??(postalCode=13029)
    # Run Keyword And Expect Error  STARTS:ValueError
    Check Object Exists    ldap://localhost:389/cn=notexisting,ou=users,dc=example,dc=com?postalCode,telephoneNumber,title??(postalCode=13029)

Check Object Count
    Check Object Count    ${LDAP_URL_SUB_MANY}  >=  1
    Check Object Count    ${LDAP_URL_SUB_MANY}  <=  5
    Run Keyword And Expect Error  Unexpected result count!*
    ...   Check Object Count    ${LDAP_URL_BASE}  <   1

Check Attribute Value
    Check Attribute Value    ${LDAP_URL}    title  matches  .*
    Check Attribute Value    ${LDAP_URL}    title  contains  buyer
    Check Attribute Value    ${LDAP_URL}    postalCode  ==  13029
    Check Attribute Value    ${LDAP_URL}    postalCode  equals  13029
    Check Attribute Value    ${LDAP_URL}    postalCode  equal  13029
    Check Attribute Value    ${LDAP_URL}    postalCode  <=  13030    
    Check Attribute Value    ${LDAP_URL}    postalCode  <  13030
    Check Attribute Value    ${LDAP_URL}    postalCode  less than  13030    
    Check Attribute Value    ${LDAP_URL}    postalCode  >=  13028
    Check Attribute Value    ${LDAP_URL}    postalCode  >  13028
    Check Attribute Value    ${LDAP_URL}    postalCode  greater than  13028
    Check Attribute Value    ${LDAP_URL}    postalCode  !=  13028
    Check Attribute Value    ${LDAP_URL}    postalCode  inequal  13028
    Check Attribute Value    ${LDAP_URL}    postalCode  should not be  13028
    Check Attribute Value    ${LDAP_URL}    telephoneNumber  *=  0049-201-555-0123
    Check Attribute Value    ${LDAP_URL}    telephoneNumber  *=  +49-201-555-0123
    Check Attribute Value    ${LDAP_URL}    telephoneNumber  contains  001-821-664-8819
    Check Attribute Value    ${LDAP_URL}    telephoneNumber  not contains  111-111-1111
    Check Attribute Value    ${LDAP_URL}    telephoneNumber  ^=  001
    Check Attribute Value    ${LDAP_URL}    telephoneNumber  starts  +49-
    Check Attribute Value    ${LDAP_URL}    telephoneNumber  starts  0049-
    Check Attribute Value    ${LDAP_URL}    telephoneNumber  should start with  0049-
    Check Attribute Value    ${LDAP_URL}    telephoneNumber  $=  0123
    Check Attribute Value    ${LDAP_URL}    telephoneNumber  ends  0123
    Check Attribute Value    ${LDAP_URL}    telephoneNumber  should end with  0123
    Run Keyword And Expect Error  *current value * mismatches with expected value*    
    ...    Check Attribute Value    ${LDAP_URL}    title  contains  seller

Check Attribute Value Count
    Check Attribute Value Count   ${LDAP_URL}  telephoneNumber  ==  4
    Check Attribute Value Count   ${LDAP_URL}  telephoneNumber  equal  4
    Run Keyword And Expect Error  Attribute value count mismatch*
    ...   Check Attribute Value Count   ${LDAP_URL}  telephoneNumber  <=  3
Check get Attribute Value Count
    ${result}  Get Attribute Value Count   ${LDAP_URL}  telephoneNumber
    Log To Console   ${result}
    Should Be Equal As Integers  ${result}  4

Check Add And Remove Attribute Value
    Add Attribute Value   ${LDAP_URL_BASE}  telephoneNumber  555-555-5555
    Check Attribute Value  ${LDAP_URL}  telephoneNumber  contains  555-555-5555
    Replace Attribute Value   ${LDAP_URL_BASE}  telephoneNumber  555-555-5555  666-666-6666
    Check Attribute Value  ${LDAP_URL}  telephoneNumber  contains  666-666-6666
    Remove Attribute Value   ${LDAP_URL_BASE}  telephoneNumber  666-666-6666
    Check Attribute Value  ${LDAP_URL}  telephoneNumber  not contains  666-666-6666
    Check Attribute Value  ${LDAP_URL}  telephoneNumber  not contains  555-555-5555
    Run Keyword And Expect Error  REGEXP:.*ScopeError.*
    ...   Add Attribute Value  ${LDAP_URL_LEVEL}  telephoneNumber  111-411-1111	

Check Overwrite Attribute Value
    Overwrite Attribute Value   ${LDAP_URL_BASE}  telephoneNumber  555-555-5555
    Check Attribute Value  ${LDAP_URL}  telephoneNumber  ==  555-555-5555
    Add Attribute Value  ${LDAP_URL_BASE}  telepohneNumber  (261)555-4472
    Add Attribute Value  ${LDAP_URL_BASE}  telepohneNumber  +49-201-555-0123
    Add Attribute Value  ${LDAP_URL_BASE}  telepohneNumber  001-821-664-8819
    Add Attribute Value  ${LDAP_URL_BASE}  telepohneNumber  0049-201-555-0123
    Run Keyword And Expect Error  REGEXP:.*ScopeError.*
    ...   Overwrite Attribute Value   ${LDAP_URL_LEVEL}  telephoneNumber  111-411-1111

Check Add Object fom LDIF File and Delete them instantly
    Add Object From LDIF   ${LDAP_URL}  ${CURDIR}${/}..${/}..${/}fake_single.ldif
    Check Attribute Value  ${LDAP_URL}  telephoneNumber  contains  555-555-5555
    Delete Object   ldap://localhost:389/cn=jmason,ou=users,dc=example,dc=com???(objectClass=*)
    Delete Object   ldap://localhost:389/cn=khernandez,ou=users,dc=example,dc=com???(objectClass=*)
    Run Keyword And Expect Error  REGEXP:.*ScopeError.*
    ...   Delete Object   ldap://localhost:389/cn=notexisting,ou=users,dc=example,dc=com??sub?(objectClass=*)

*** Keywords ***
Set up
    # [Arguments]    ${MOKAPI_PATH}    ${PROV_FILE}
    ${mokapi}=    Start Process  ${MOKAPI_PATH}  --providers-file-filename  ${PROV_FILE}  shell
    # Connect    ${LDAP_URL}    ${BIND_DN}    ${PASSWORD}  # ${CERT} 
    Connect    
    ...  ldap_url=${LDAP_URL}
    ...  bind_dn=${BIND_DN}
    ...  password=${PASSWORD}
    Log Many    ${mokapi.stdout}    ${mokapi.stderr}

Clean up
    # [Arguments]    ${mokapi}
    disconnect    ${LDAP_URL}
    Terminate Process  ${mokapi} 
    # Log Many    ${mokapi.stdout}    ${mokapi.stderr}
