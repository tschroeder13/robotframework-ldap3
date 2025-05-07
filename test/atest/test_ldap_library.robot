*** Settings ***
Library    Ldap3Library  
Library    Process
Suite Setup    Set up
Suite Teardown    Clean up

*** Variables ***
${MOKAPI_PATH}=  D:${/}idmHelpers${/}PortableApps${/}mokapi_v0.15.0_windows_amd64${/}mokapi.exe
${PROV_FILE}=  D:${/}git_workspace${/}robotframework-ldap3${/}test${/}mocks${/}ldap.yaml
${LDAP_URL_BASE}=  ldap://localhost:389/cn=tfoster,ou=users,dc=example,dc=com?postalCode,telephoneNumber??(postalCode=13029)
${LDAP_URL_SUB}=  ldap://localhost:389/ou=users,dc=example,dc=com?postalCode,telephoneNumber?sub?(postalCode=13029)
${LDAP_URL_LEVEL}=  ldap://localhost:389/ou=users,dc=example,dc=com?postalCode,telephoneNumber?one?(postalCode=13029)
${LDAP_URL}=  ${LDAP_URL_BASE}
${BIND_DN}=  cn=admin,dc=example,dc=com
${PASSWORD}=  P4ssW0rd!
${CERT}=  n/a
${mokapi}=  None

*** Test Cases ***
Search LDAP with subtree scope
    Search    ${LDAP_URL_SUB}

Search LDAP with base scope
    Search    ${LDAP_URL_BASE}

Search LDAP with one level scope
    Search    ${LDAP_URL_LEVEL}

Check Attribute Value
    # Check Attribute Value    ${LDAP_URL}    titel  matches  .*
    # Check Attribute Value    ${LDAP_URL}    postalCode  ==  13029
    # Check Attribute Value    ${LDAP_URL}    postalCode  equals  13029
    # Check Attribute Value    ${LDAP_URL}    postalCode  equal  13029
    # Check Attribute Value    ${LDAP_URL}    postalCode  <=  13030    
    # Check Attribute Value    ${LDAP_URL}    postalCode  <  13030
    # Check Attribute Value    ${LDAP_URL}    postalCode  less than  13030    
    # Check Attribute Value    ${LDAP_URL}    postalCode  >=  13028
    # Check Attribute Value    ${LDAP_URL}    postalCode  >  13028
    # Check Attribute Value    ${LDAP_URL}    postalCode  greater than  13028
    # Check Attribute Value    ${LDAP_URL}    postalCode  !=  13028
    # Check Attribute Value    ${LDAP_URL}    postalCode  inequal  13028
    # Check Attribute Value    ${LDAP_URL}    postalCode  should not be  13028
    # Check Attribute Value    ${LDAP_URL}    telephoneNumber  *=  +49-201-555-0123
    # Check Attribute Value    ${LDAP_URL}    telephoneNumber  contains  +49-201-555-0123
    # Check Attribute Value    ${LDAP_URL}    telephoneNumber  not contains  111-111-1111
    Check Attribute Value    ${LDAP_URL}    telephoneNumber  ^=  +49-
    # Check Attribute Value    ${LDAP_URL}    telephoneNumber  starts  +49-
    # Check Attribute Value    ${LDAP_URL}    telephoneNumber  should start with  +49-
    # Check Attribute Value    ${LDAP_URL}    telephoneNumber  $=  0123
    # Check Attribute Value    ${LDAP_URL}    telephoneNumber  ends  0123
    # Check Attribute Value    ${LDAP_URL}    telephoneNumber  should end with  0123







*** Keywords ***
Set up
    # [Arguments]    ${MOKAPI_PATH}    ${PROV_FILE}
    ${mokapi}=    Start Process  ${MOKAPI_PATH}  --providers-file-filename  ${PROV_FILE}  shell
    connect    ${LDAP_URL}    ${BIND_DN}    ${PASSWORD}  # ${CERT} 
    Log Many    ${mokapi.stdout}    ${mokapi.stderr}

Clean up
    # [Arguments]    ${mokapi}
    disconnect    ${LDAP_URL}
    Terminate Process  ${mokapi} 
    # Log Many    ${mokapi.stdout}    ${mokapi.stderr}
