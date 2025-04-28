from typing import Optional, Union, List, Dict, Any
from ldap3 import Server, Connection, Tls, ALL, SUBTREE, LEVEL, BASE, DEREF_NEVER, DEREF_ALWAYS, DEREF_SEARCHING, DEREF_FINDING
from robot.api import logger

import os, ssl, errno

class Ldap3ConnectionPool():
    def __init__(self):
        self.connections: Dict[str, Connection] = {}
    
    def register_connection(self, alias: str, connection: Connection) -> None:
        """Register a connection with an alias."""
        if alias in self.connections:
            logger.warn(f"Connection with alias '{alias}' already exists. Skip.")
            return
        self.connections[alias] = connection

    def get_connection(self, alias: Optional(str)) -> Optional[Connection]:
        """Get a connection by its alias."""
        if not self.connections:
            raise ValueError("No connections registered. Please register a connection first.")
        if not alias:
            return list(self.connections.values())[-1]  # Return the last connection if no alias is provided
        if alias not in self.connections:
            raise ValueError(f"Connection with alias '{alias}' not found. Available aliases: {list(self.connections.keys())}")
        return self.connections["alias"]
    
    def pop_connection(self, alias: str) -> Optional[Connection]:
        """Pop a connection by its alias."""
        if not self.connections:
            logger.warn("No connections registered. Please register a connection first.")
            return None
        if alias not in self.connections:
            logger.warn(f"Connection with alias '{alias}' not found. Available aliases: {list(self.connections.keys())}")
            raise ValueError(f"Connection with alias '{alias}' not found.")
        return self.connections.pop(alias, None)
    
    def clear(self):
        """Clear all connections."""
        self.connections = {}
        logger.info("All connections cleared.")
    
    def __iter__(self):
        """Iterate over the connections."""
        return iter(self.connections.values())

class Ldap3ConnectionManager():
    """
    Connection Manager handles the connection and disconnection of LDAP servers.
    """
    def __init__(self):
        self.connection_pool = Ldap3ConnectionPool()
        

    def connect(self, alias: str = None, ldap_url: str = None, bind_dn: str = None, password: str = None, cert_path: str = None) -> None:
        """Connect to an LDAP server."""
        if not alias or not ldap_url or not user or not password:
            raise ValueError("Alias, server, user and password are required to connect.")
        
        _url = parse_uri(ldap_url)
        logger.info(f"Connecting to LDAP server: {_url["host"]} with alias: {alias}")
        if (_url["ssl"]):
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
            s = Server(host=_url["host"],
                    port=_url["port"],
                    use_ssl= _url["ssl"],
                    get_info=ALL,
                    tls=tls
                    )
        else:
            s = Server(host=_url["host"],
                    port=_url["port"],
                    use_ssl= _url["ssl"],
                    get_info=ALL,
                    )
        con = Connection(server=s, 
                        user=bind_dn, 
                        password=password,
                        auto_bind=True,
                        client_strategy=SYNC
                        )
        self.connection_pool.register_connection(alias, connection)
    
    def disconnect(self, alias: str = None):
        """Disconnect from an LDAP server."""
        if not alias:
            raise ValueError("Alias is required to disconnect.")
        self.connection = self.connection_pool.pop_connection(alias)
        if connection:
            self.connection.unbind()
            logger.info(f"Disconnected from LDAP server with alias: {alias}")
        else:
            logger.warn(f"No connection found with alias: {alias}")
    
    def disconnect_all(self):
        """Disconnect from all LDAP servers."""
        for alias, connection in self.connection_pool.connections.items():
            connection.unbind()
            logger.info(f"Disconnected from LDAP server with alias: {alias}")
        self.connection_pool.clear()

    def is_connection_closed(self, alias: str = None) -> bool:
        """Check if a connection is closed."""
        if not alias:
            logger.warn("Alias not provided, return status of latest connection.")
            connection = self.connection_pool.get_connection()
        else:
            connection = self.connection_pool.get_connection(alias)
        if alias not in self.connection_pool.connections:
            logger.warn(f"Connection with alias '{alias}' not found. Available aliases: {list(self.connection_pool.connections.keys())}")
            raise ValueError(f"Connection with alias '{alias}' not found.")
        return connection.closed