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

from typing import Optional,Dict
from ldap3 import Server, Connection, Tls, ALL, SYNC, BASE
from ldap3.utils.uri import parse_uri as ldap3_parse_uri
from robot.api import logger

import os, ssl, errno

class Ldap3ConnectionPool():
    
    def __init__(self):
        self.connections: Dict[str, Connection] = {}

    def register_connection(self, host: str, connection: Connection) -> None:
        """Register a connection with an alias."""
        if host in self.connections:
            logger.warn(f"Connection with alias '{host}' already exists. Skip.")
            return
        self.connections[host] = connection

    def get_connection(self, host: Optional[str]=None) -> Optional[Connection]:
        """Get a connection by its alias."""
        if not self.connections:
            raise ValueError("No connections registered. Please register a connection first.")
        if not host:
            return list(self.connections.values())[-1]  # Return the last connection if no alias is provided
        if host not in self.connections:
            raise ValueError(f"Connection with alias '{host}' not found. Available aliases: {list(self.connections.keys())}")
        return self.connections[host]
    
    def pop_connection(self, host: str) -> Optional[Connection]:
        """Pop a connection by its alias."""
        if not self.connections:
            logger.warn("No connections registered. Please register a connection first.")
            return None
        if host not in self.connections:
            logger.warn(f"Connection with alias '{host}' not found. Available aliases: {list(self.connections.keys())}")
            raise ValueError(f"Connection with alias '{host}' not found.")
        return self.connections.pop(host, None)
    
    def clear(self):
        """Clear all connections."""
        self.connections = {}
        logger.info("All connections cleared.")
    
    def __iter__(self):
        """Iterate over the connections."""
        return iter(self.connections.values())

class Ldap3ConnectionManager():
    """
    With Connection Manager one can connect and disconnect to and from a LDAP server.

    The Connection Manager is a singleton class that manages the connection pool.
    It provides methods to connect, disconnect, and check the status of connections.
    """
    
    connection_pool = Ldap3ConnectionPool()

    
    def __init__(self):
        pass

    @staticmethod
    def parse_uri(ldap_url: str):
        parsed_url = ldap3_parse_uri(ldap_url)
        if parsed_url['scope'] == '':
            parsed_url['scope'] = BASE
        return parsed_url

    def connect(self, ldap_url: str = None, 
                bind_dn: str = None, 
                password: str = None, 
                cert_path: Optional[str] = None) -> None:
        """Connect to an LDAP server.
        Parameters:
        - ldap_url: The LDAP URL to connect to.
        - bind_dn: The bind DN to use for authentication.
        - password: The password to use for authentication.
        - cert_path: The path to the root certificate for secure connection (optional).
        
        Registers the connection with the host as an alias in the connection pool.
        Raises:
        - ValueError: If ldap_url, bind_dn, or password is not provided.
        - FileNotFoundError: If the root certificate is not found.
        - Forwards LDAP Exceptions if the connection fails.

        Example:
        | Connect    
        | ...  ldap_url=${LDAP_URL}
        | ...  bind_dn=${BIND_DN}
        | ...  password=${PASSWORD}        
        """
        if not ldap_url or not bind_dn or not password:
            raise ValueError("Ldap_url, bind_dn and password are required to connect.")
        
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        logger.info(f"Connecting to LDAP server: {_url['host']}")
        if (_url['ssl']):
            if cert_path is None:
                raise ValueError(f"Missing root certificate for {ldap_url} connection.")
            ca = os.path.abspath(cert_path) 
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ctx.verify_mode = ssl.CERT_REQUIRED
            ctx.load_verify_locations(ca)
            tls = Tls(ca_certs_file=ca,
                ciphers=('AES256-GCM-SHA384'), 
                validate=ssl.CERT_REQUIRED, 
                version=ssl.PROTOCOL_TLSv1_2
                )
            if tls.ca_certs_file == None: raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), )
            s = Server(host=_url['host'],
                    port=_url['port'],
                    use_ssl= _url['ssl'],
                    get_info=ALL,
                    tls=tls
                    )
        else:
            s = Server(host=_url['host'],
                    port=_url['port'],
                    use_ssl= _url['ssl'],
                    get_info=ALL,
                    )
        con = Connection(server=s, 
                        user=bind_dn, 
                        password=password,
                        auto_bind=True,
                        client_strategy=SYNC
                        )
        self.connection_pool.register_connection(_url['host'], con)
    
    def disconnect(self, ldap_url: str = None):
        """Disconnect from an LDAP server.
        Parameters:
        - ldap_url: The LDAP URL to disconnect from.
        Raises:
        - ValueError: If ldap_url is not provided.
        
        Unbinds the connection stated with the URL and removes it from the connection pool.
        Example:
        | Disconnect ldap://localhost:389/cn=admin,dc=example,dc=com???(objectClass=*)
        """
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        if not ldap_url:
            raise ValueError("Ldap_url is required to disconnect.")
        connection = self.connection_pool.pop_connection(_url['host'])
        if connection:
            connection.unbind()
            logger.info(f"Disconnected from LDAP server: {_url['host']}")
        else:
            logger.warn(f"No connection found for: {_url['host']}")
    
    def disconnect_all(self):
        """Unbinds all LDAP connections and cleares the connection pool.
        Example:
        | Disconnect all
        """
        for alias, connection in self.connection_pool.connections.items():
            connection.unbind()
            logger.info(f"Disconnected from LDAP server with alias: {alias}")
        self.connection_pool.clear()

    def is_connection_closed(self, ldap_url: str = None) -> bool:
        """Check if a connection is closed.
        Parameters:
        - ldap_url: The LDAP URL to check the connection status.
        Returns:
        - True if the connection is closed, False otherwise.
        Raises:
        - ValueError: If ldap_url is not provided.
        Example:
        | ${status}=    Is Connection Closed    ldap://localhost:389/cn=admin,dc=example,dc=com???(objectClass=*)
        """
        if not ldap_url:
            logger.warn("Ldap_url not provided, return status of latest connection.")
            connection = self.connection_pool.get_connection()
        else:
            _url = Ldap3ConnectionManager.parse_uri(ldap_url)
            connection = self.connection_pool.get_connection(_url['host'])
        # if alias not in self.connection_pool.connections:
        #     logger.warn(f"Connection with alias '{alias}' not found. Available aliases: {list(self.connection_pool.connections.keys())}")
        #     raise ValueError(f"Connection with alias '{alias}' not found.")
        return connection.closed