*** Settings ***
Library    Ldap3Library  
Library    Process
Suite Setup    Run Mokapi    ${MOKAPI_PATH}    ${PROV_FILE}
Suite Teardown    Terminate Process    ${mokapi}

*** Variables ***
${MOKAPI_PATH}=  D:${/}idmHelpers${/}PortableApps${/}mokapi_v0.15.0_windows_amd64${/}mokapi.exe
${PROV_FILE}=  D:${/}git_workspace${/}robotframework-ldap3${/}test${/}mocks${/}ldap.yaml
${LDAP_URL_BASE}=  ldap://localhost:389/cn=tfoster,ou=users,dc=example,dc=com?postalCode??(postalCode=13029)
${LDAP_URL_SUB}=  ldap://localhost:389/ou=users,dc=example,dc=com?postalCode?sub?(postalCode=13029)
${LDAP_URL_LEVEL}=  ldap://localhost:389/ou=users,dc=example,dc=com?postalCode?one?(postalCode=13029)
${LDAP_URL}=  ${LDAP_URL_BASE}
${BIND_DN}=  cn=admin,dc=example,dc=com
${PASSWORD}=  P4ssW0rd!
${CERT}=  n/a
${mokapi}=  None

*** Test Cases ***
Test LDAP Connection
    connect    ${LDAP_URL}    ${BIND_DN}    ${PASSWORD}  # ${CERT} 
    Search    ${LDAP_URL}
    Check Attribute Value    ${LDAP_URL}    postalCode  ==  13029
    Check Attribute Value    ${LDAP_URL}    postalCode  <=  13030
    Check Attribute Value    ${LDAP_URL}    postalCode  >=  13028
    Check Attribute Value    ${LDAP_URL}    postalCode  <  13030
    Check Attribute Value    ${LDAP_URL}    postalCode  >  13028
    Check Attribute Value    ${LDAP_URL}    postalCode  !=  13028
    disconnect    ${LDAP_URL}




*** Keywords ***
Run Mokapi
    [Arguments]    ${MOKAPI_PATH}    ${PROV_FILE}
    ${mokapi}=    Start Process  ${MOKAPI_PATH}  --providers-file-filename  ${PROV_FILE}  shell
    Log Many    ${mokapi.stdout}    ${mokapi.stderr}

