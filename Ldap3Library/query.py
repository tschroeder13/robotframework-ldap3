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

from robot.api import logger
from ldap3 import Connection, MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE, BASE
from Ldap3Library.connection_manager import Ldap3ConnectionManager
from assertionengine import AssertionOperator, verify_assertion
from typing import Any, Optional, List, Union
from ldif import LDIFParser


class Ldap3Query():

    LDIF = "ldif"
    JSON = "json"
    ENTRIES = "entries"

    """Class to handle LDAP queries."""

    def __init__(self):
        self.connection_pool = Ldap3ConnectionManager.connection_pool

    _multi_value_assertions = [
        AssertionOperator["*="],
        AssertionOperator["contains"],
        AssertionOperator["not contains"]
    ]

    def _is_base_scope(self, ldap_url: str) -> Any:
        """Check if the scope is BASE."""
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        if not _url["scope"] == BASE:
            logger.error(
                f"ScopeError: Scope must be BASE for single object actions. Current scope: {_url['scope']}")
            raise ValueError(
                f"ScopeError: Scope must be BASE for single object actions. Current scope: {_url['scope']}")
        return _url

    def search(self, ldap_url: str, return_type: str = LDIF) -> Union[List[dict], List[str], str]:
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        connection: Connection = self.connection_pool.get_connection(
            _url["host"])
        connection.search(search_base=_url["base"],
                          search_filter=_url["filter"],
                          search_scope=_url["scope"],
                          attributes=_url["attributes"])
        logger.info(
            f"Search results: {len(connection.entries)} entries found.")
        match return_type:
            case self.LDIF:
                return connection.response_to_ldif()
            case self.JSON:
                return connection.response_to_json()
            case self.ENTRIES:
                return connection.entries
            case _:
                raise ValueError(
                    f"Invalid return type: {return_type}. Must be one of {self.LDIF}, {self.JSON}, or {self.ENTRIES}.")

    def check_object_exists(self, ldap_url: str):
        _url = self._is_base_scope(ldap_url)
        entries = self.search(ldap_url, self.ENTRIES)
        exists = ((len(entries) == 1) and
                  (entries[0].entry_dn == _url["base"])
                  )
        if not exists:
            logger.info(f"Object {_url['base']} does not exist.")
            return False
        logger.info(f"Object {_url['base']} exists: {exists}")
        return exists

    def check_object_count(self, ldap_url: str,
                           assertion_operator: AssertionOperator,
                           expected_count: int,
                           assertion_message: str = None):
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        entries = self.search(ldap_url, self.ENTRIES)
        # connection: Connection = self.connection_pool.get_connection(_url["host"])
        # connection.search(search_base=_url["base"],
        #                   search_filter=_url["filter"],
        #                   search_scope=_url["scope"],
        #                   attributes=_url["attributes"])
        actual_count = len(entries)
        verify_assertion(actual_count, assertion_operator, expected_count,
                         "Unexpected result count!", assertion_message)
        logger.info(
            f"Expected count: {expected_count}, Actual count: {actual_count}")
        return True

    def check_attribute_value(self, ldap_url: str,
                              attribute_name: str,
                              assertion_operator: AssertionOperator,
                              expected_value: Any,
                              assertion_message: str = None):
        result = False
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        entries = self.search(ldap_url, self.ENTRIES)
        if attribute_name not in _url["attributes"]:
            raise ValueError(
                f"Attribute {attribute_name} not found in the LDAP URL: {ldap_url}")
        if attribute_name not in entries[0].entry_attributes:
            raise ValueError(
                f"Attribute {attribute_name} not found in the LDAP entry: {ldap_url}")
        if len(entries) < 1:
            raise ValueError(
                f"No entries found for the given LDAP URL: {ldap_url}")
        if len(entries) > 1:
            raise ValueError(
                f"Multiple entries found for the given LDAP URL: {ldap_url}")
        actual_value = entries[0][attribute_name].value
        if isinstance(actual_value, list) and assertion_operator not in self._multi_value_assertions:
            for i, value in enumerate(actual_value):
                try:
                    verify_assertion(value=value, operator=assertion_operator, expected=expected_value,
                                     custom_message="Attribute value mismatch", message=assertion_message)
                    logger.info(
                        f"Expected value: {expected_value}, Actual value: {value}")
                    return True
                    # break
                except AssertionError as e:
                    logger.info(f"Assertion failed: {e}")
                    result = False
                    if i < len(actual_value) - 1:
                        continue
                    else:
                        raise AssertionError() from e
        else:
            verify_assertion(value=actual_value,
                             operator=assertion_operator,
                             expected=expected_value,
                             custom_message=f"{attribute_name}'s current value {actual_value} mismatches with expected value {expected_value}",
                             message=assertion_message)
            logger.info(
                f"Expected value: {expected_value}, Actual value: {actual_value}")
            return True
        # return actual_value == expected_value, f"Attribute value mismatch: expected {expected_value} {assertion_operator.value} {actual_value}"
        return result

    def check_attribute_value_count(self, ldap_url: str,
                                    attribute_name: str,
                                    assertion_operator: AssertionOperator,
                                    expected_value: Any,
                                    assertion_message: str = None):
        _expected = int(expected_value)
        if not isinstance(_expected, int):
            raise ValueError(
                f"Expected value must be an integer. Got {type(_expected)}")
        self._is_base_scope(ldap_url)
        entries = self.search(ldap_url, self.ENTRIES)
        value_cnt = len(entries[0][attribute_name].values)
        if not value_cnt or value_cnt < 1:
            raise ValueError(
                f"Attribute {attribute_name} not found in the LDAP entry: {ldap_url}")
        verify_assertion(value=value_cnt,
                         operator=assertion_operator,
                         expected=_expected,
                         custom_message=f"Attribute value count mismatch! {value_cnt} {assertion_operator.value} {_expected}",
                         message=assertion_message)
        return True

    def get_attribute_value_count(self, ldap_url: str,
                                  attribute_name: str) -> int:
        entries = self.search(ldap_url, self.ENTRIES)
        self._is_base_scope(ldap_url)
        if not attribute_name in entries[0].entry_attributes:
            raise ValueError(
                f"Attribute {attribute_name} not found in the LDAP entry: {ldap_url}")
        value_cnt = len(entries[0][attribute_name].values)
        return value_cnt

    def add_attribute_value(self, ldap_url: str,
                            attribute_name: str,
                            attribute_value: str
                            ):
        _url = self._is_base_scope(ldap_url)
        connection: Connection = self.connection_pool.get_connection(
            _url["host"])
        if not connection.modify(dn=_url["base"],
                                 changes={attribute_name: [(MODIFY_ADD, [attribute_value])]}):
            raise ValueError(
                f"Failed to add attribute {attribute_name} with value {attribute_value} to {ldap_url}. Error: {connection.result['description']}")
        logger.info(
            f"Added attribute {attribute_name} with value {attribute_value} to {ldap_url}.")
        return True

    def remove_attribute_value(self, ldap_url: str,
                               attribute_name: str,
                               attribute_value: str):
        _url = self._is_base_scope(ldap_url)
        connection: Connection = self.connection_pool.get_connection(
            _url["host"])
        if not connection.modify(_url["base"],
                                 changes={attribute_name: [(MODIFY_DELETE, [attribute_value])]}):
            raise ValueError(
                f"Failed to remove attribute {attribute_name} with value {attribute_value} from {ldap_url}. Error: {connection.result['description']}")
        logger.info(
            f"Removed attribute {attribute_name} with value {attribute_value} from {ldap_url}.")
        return True

    def replace_attribute_value(self, ldap_url: str,
                                attribute_name: str,
                                old_value: str,
                                new_value: str):
        _url = self._is_base_scope(ldap_url)
        connection: Connection = self.connection_pool.get_connection(
            _url["host"])
        if not connection.modify(dn=_url["base"],
                                 changes={attribute_name: [(MODIFY_DELETE, [old_value])]}):
            raise ValueError(
                f"Failed to add attribute {attribute_name} with value {old_value} to {ldap_url}. Error: {connection.result['description']}")
        if not connection.modify(dn=_url["base"],
                                 changes={attribute_name: [(MODIFY_ADD, [new_value])]}):
            raise ValueError(
                f"Failed to add attribute {attribute_name} with value {new_value} to {ldap_url}. Error: {connection.result['description']}")
        logger.info(
            f"Replaced attribute {attribute_name} from {old_value} to {new_value} in {ldap_url}.")
        return True

    def overwrite_attribute_value(self, ldap_url: str,
                                  attribute_name: str,
                                  attribute_value: str):
        _url = self._is_base_scope(ldap_url)
        connection: Connection = self.connection_pool.get_connection(
            _url["host"])
        if not connection.modify(dn=_url["base"],
                                 changes={attribute_name: [(MODIFY_REPLACE, [attribute_value])]}):
            raise ValueError(
                f"Failed to add attribute {attribute_name} with value {attribute_value} to {ldap_url}. Error: {connection.result['description']}")
        logger.info(
            f"Replaced attribute {attribute_name} with value {attribute_value} in {ldap_url}.")
        return True

    def add_object_from_ldif(self, ldap_url: str, ldif_file: str, object_class: Optional[str] = "inetOrgPerson"):
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        connection: Connection = self.connection_pool.get_connection(
            _url["host"])
        parser = LDIFParser(open(ldif_file, "rb"))
        for dn, record in parser.parse():
            if not connection.add(dn=dn,
                                  object_class=object_class,
                                  attributes=record):
                raise ValueError(
                    f"Failed to add object from LIDF to {ldap_url}. Error: {connection.result['description']}")
            logger.info(f"Added object from LIDF to {ldap_url}.")
        return True

    def delete_object(self, ldap_url: str):
        _url = self._is_base_scope(ldap_url)
        connection: Connection = self.connection_pool.get_connection(
            _url["host"])
        if not connection.delete(dn=_url["base"]):
            logger.error(
                f"Failed to delete object {ldap_url}. Error: {connection.result['description']}")
            raise ValueError(
                f"Failed to delete object {ldap_url}. Error: {connection.result['description']}")
        logger.info(f"Deleted object {ldap_url}.")
        return True
