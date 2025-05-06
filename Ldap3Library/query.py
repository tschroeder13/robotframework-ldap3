from robot.api import logger
from ldap3 import Connection, BASE, SUBTREE, LEVEL, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES, ALL
from Ldap3Library.connection_manager import Ldap3ConnectionManager
from assertionengine import AssertionOperator, verify_assertion
from typing import Any, Optional, List, Union
class Ldap3Query():
    """Class to handle LDAP queries."""
    def __init__(self):
        self.connection_pool = Ldap3ConnectionManager.connection_pool
    # def __init__(self, connectionManager: Optional[Ldap3ConnectionManager]=None):
    #     self.connectionManager = connectionManager
    #     self.connection_pool = self.connectionManager.connection_pool

    def search(self, ldap_url: str):
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        connection: Connection = self.connection_pool.get_connection(_url["host"])
        connection.search(search_base=_url["base"], 
                          search_filter=_url["filter"], 
                          search_scope=_url["scope"], 
                          attributes=_url["attributes"])
        logger.info(f"Search results: {len(connection.entries)} entries found.")
        return connection.entries
    
    
    def object_exists(self, ldap_url: str):
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        connection: Connection = self.connection_pool.get_connection(_url["host"])
        connection.search(search_base=_url["base"], 
                          search_filter=_url["filter"], 
                          search_scope=_url["scope"], 
                          attributes=_url["attributes"])
        exists = (len(connection.entries) == 1) and (connection.entries[0].entry_dn == _url["base"])
        logger.info(f"Object {_url['base']} exists: {exists}")
        return exists
    
    def check_object_count(self, ldap_url: str, 
                           assertion_operator: AssertionOperator, 
                           expected_count: int,
                           assertion_message: str = None):
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        connection: Connection = self.connection_pool.get_connection(_url["host"])
        connection.search(search_base=_url["base"], 
                          search_filter=_url["filter"], 
                          search_scope=_url["scope"], 
                          attributes=_url["attributes"])
        actual_count = len(connection.entries)
        logger.info(f"Expected count: {expected_count}, Actual count: {actual_count}")
        return verify_assertion(actual_count, assertion_operator, expected_count, "Unexpected result count!", assertion_message)
    
    def check_attribute_value(self, ldap_url: str, 
                              attribute_name: str,
                            assertion_operator: AssertionOperator, 
                            expected_value: Any, 
                            assertion_message: str = None):
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        entries = self.search(ldap_url)
        if attribute_name not in _url["attributes"]:
            raise ValueError(f"Attribute {attribute_name} not found in the LDAP URL: {ldap_url}")
        if attribute_name not in entries[0].entry_attributes:
            raise ValueError(f"Attribute {attribute_name} not found in the LDAP entry: {ldap_url}")
        if len(entries) < 1:
            raise ValueError(f"No entries found for the given LDAP URL: {ldap_url}")
        if len(entries) > 1:
            raise ValueError(f"Multiple entries found for the given LDAP URL: {ldap_url}")
        actual_value = entries[0][attribute_name].value
        result = verify_assertion(actual_value, 
                                  assertion_operator, 
                                  expected_value, 
                                  "Unexpected attribute value!", 
                                  assertion_message)
        logger.info(f"Expected value: {expected_value}, Actual value: {actual_value}")
        # return actual_value == expected_value, f"Attribute value mismatch: expected {expected_value} {assertion_operator.value} {actual_value}"
        return result
    
    def add_attribute_value(self, ldap_url: str, 
                     attribute_name: str, 
                     attribute_value: str):
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        connection: Connection = self.connection_pool.get_connection(_url["host"])
        if not connection.add(_url["base"], 
                              attributes={attribute_name: attribute_value}):
            raise ValueError(f"Failed to add attribute {attribute_name} with value {attribute_value} to {ldap_url}. Error: {connection.result['description']}")
        logger.info(f"Added attribute {attribute_name} with value {attribute_value} to {ldap_url}.")
        return True
    
    def replace_attribute_value(self, ldap_url: str, 
                        attribute_name: str, 
                        old_value: str, 
                        new_value: str):
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        connection: Connection = self.connection_pool.get_connection(_url["host"])
        if not connection.modify(_url["base"], 
                                 {'replace': {attribute_name: [old_value, new_value]}}):
            raise ValueError(f"Failed to replace attribute {attribute_name} from {old_value} to {new_value} in {ldap_url}. Error: {connection.result['description']}")
        logger.info(f"Replaced attribute {attribute_name} from {old_value} to {new_value} in {ldap_url}.")
        return True
    
    def remove_attribute_value(self, ldap_url: str, 
                        attribute_name: str, 
                        attribute_value: str):
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        connection: Connection = self.connection_pool.get_connection(_url["host"])
        if not connection.modify(_url["base"], 
                                 {'delete': {attribute_name: attribute_value}}):
            raise ValueError(f"Failed to remove attribute {attribute_name} with value {attribute_value} from {ldap_url}. Error: {connection.result['description']}")
        logger.info(f"Removed attribute {attribute_name} with value {attribute_value} from {ldap_url}.")
        return True
    
