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
    Connection Manager handles the connection and disconnection of LDAP servers.
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
        """Connect to an LDAP server."""
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
        _url = Ldap3ConnectionManager.parse_uri(ldap_url)
        """Disconnect from an LDAP server."""
        if not ldap_url:
            raise ValueError("Ldap_url is required to disconnect.")
        connection = self.connection_pool.pop_connection(_url['host'])
        if connection:
            connection.unbind()
            logger.info(f"Disconnected from LDAP server: {_url['host']}")
        else:
            logger.warn(f"No connection found for: {_url['host']}")
    
    def disconnect_all(self):
        """Disconnect from all LDAP servers."""
        for alias, connection in self.connection_pool.connections.items():
            connection.unbind()
            logger.info(f"Disconnected from LDAP server with alias: {alias}")
        self.connection_pool.clear()

    def is_connection_closed(self, ldap_url: str = None) -> bool:
        """Check if a connection is closed."""
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