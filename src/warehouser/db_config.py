from sqlalchemy import Engine, create_engine
from warehouser.util import get_keys
from typing import Literal, Optional, TypeAlias, get_args



supportedDialects = Literal['mysql', 'postgresql', 'doris', 'sqlite']
dbmsConfigDict = dict[Literal['host', 'port', 'user', 'password'], str]
dbConfigDict: TypeAlias = dict[Literal['dbms', 'host', 'port', 'user', 'password', 'database'], str]


MYSQL_DEFAULT_PORT = "3306"
PG_DEFAULT_PORT = "5432"
DORIS_DEFULT_PORT = "9030"


MYSQL_ENGINE = 'pymysql'

portType: TypeAlias = str|int

def _default_host(dialect:supportedDialects) -> str:
    if dialect == 'sqlite':
        return ''
    return 'localhost'

def _default_port(dialect:supportedDialects) -> str:
    match dialect:
        case 'mysql':
            return MYSQL_DEFAULT_PORT
        case 'postgresql':
            return PG_DEFAULT_PORT
        case 'doris':
            return DORIS_DEFULT_PORT
        case 'sqlite':
            return ''
    raise SyntaxError(f'Unsupported RDBMS: {dialect}')


def _dialect_engine_str(dialect:supportedDialects) -> str:
    match dialect:
        case 'mysql':
            return f'mysql+{MYSQL_ENGINE}'
        case 'postgresql':
            return 'postgresql+psycopg2'
        case 'doris':
            return f'doris+{MYSQL_ENGINE}'
        case 'sqlite':
            return 'sqlite'
    raise SyntaxError(f'Unsupported RDBMS: {dialect}')


class WarehouserConfig:
    """DBmanager config class.
    Contains full database config data, needed for connection and vendor specific logic.
    Contains fields:
        dialect (str): SQL  dialect name. Can be on of: ['mysql', 'postgresql', 'doris', 'sqlite']\n
        host (str): DBMS host\n
        port (str): DBMS port\n
        user (str): DBMS user name\n
        pwd (str): DBMS user password\n
        database (str, optional): Database name to be used in connection. Defaults to None.
    """
    def __init__(self, dialect: supportedDialects, database: str, user: str, pwd: str, /, *,
                 host: Optional[str] = None,
                 port: Optional[portType] = None
                 ) -> None:
        """Creates config object for DBmanager.

        Args:
            dbms (str): Database management system name. Can be on of: ['mysql', 'postgresql']
            host (str): DBMS host
            port (str): DBMS port
            user (str): DBMS user name
            pwd (str): DBMS user password
            database (str, optional): Database name to be used in connection. Defaults to None.
        """
        assert dialect in get_args(supportedDialects), f'Unsupported DBMS literal. Must be one of: {get_args(supportedDialects)}'
        self.__dialect: supportedDialects = dialect
        self.__host: str = host if host else _default_host(dialect)
        self.__port: str = str(port) if port else _default_port(dialect)
        self.__user: str = user
        self.__pwd: str  = pwd
        self.__database: str = database
    
    
    @property
    def dialect(self) -> supportedDialects:
        return self.__dialect
    
    @property
    def host(self) -> str:
        return self.__host
    
    @property
    def port(self) -> str:
        return self.__port
    
    @property
    def user(self) -> str:
        return self.__user
    
    @property
    def pwd(self) -> str:
        return self.__pwd
    
    @property
    def database(self) -> str:
        return self.__database
    
    @database.setter
    def database(self, database_name: str):
        self.__database = database_name
        
    
    def address_login_str(self) -> str:
        return f'{self.user}:{self.pwd}@{self.host}:{self.port}'
    
    
    def engine_str(self, database: Optional[str] = None):
        _database = database if database else self.database
        return WarehouserConfig.make_eng_str(self.dialect, self.address_login_str(), database=_database)
    
    def engine(self, database: Optional[str] = None) -> Engine:
        return create_engine(self.engine_str(database))
    
    def db_params(self) -> tuple[str, str, str, str]:
        """Returns tuple with (host, port, user, password) - Config parameters for current DB.

        Returns:
            
            tuple[str, str, str, str]: Resulting tuple.
        """        
        return (self.host, self.port, self.user, self.pwd)
    
    
    def __repr__(self) -> str:
        eng_str = self.engine_str()
        return 'WarehouserConfig[{}:"{}"]'.format(self.dialect, eng_str)
    
    @staticmethod
    def make_eng_str(rdbms:supportedDialects, 
                    address_login_str: str,
                    *,
                    database:Optional[str]=None) -> str:
        """Creates sqlalchemy Engine for use in DBmanager

        Args:
            rdbms ('mysql'|'postgres'): RDBMS to be used in engine
            user (str): DB user
            password (str): Password for user
            host (str): DB host
            port (str, optional): DB host port. If None - default port for chosen RDBMS will be used. Defaults to None.
            database (str, optional): Database to be connected to. If None - connection to RDBMS root. Defaults to None.

        Returns:
            Engine: sqlalchemy engine class.
        """
        engine_type = _dialect_engine_str(rdbms)
        dbstr = f'/{database}' if database else ''
        return f'{engine_type}://{address_login_str}{dbstr}'


class SqliteWhConfig(WarehouserConfig):
    def __init__(self, database: str) -> None:
        super().__init__('sqlite', database, '', '')
    
    def address_login_str(self) -> str:
        return ''
    
    # def engine_str(self, database: Optional[str] = None):
    #     _database = database if database else self.database
    #     # return WarehouserConfig.make_eng_str(self.dialect, self.user, self.pwd, self.host, self.port, database=_database)
    #     return f'sqlite:///{_database}'




def config_from_dict(config_dict: dbConfigDict, /) -> WarehouserConfig:
    d = config_dict
    assert 'dbms' in d,     'Missing "dbms" field in DB config!'
    assert 'host' in d,     'Missing "host" field in DB config!'
    assert 'user' in d,     'Missing "user" field in DB config!'
    assert 'password' in d, 'Missing "password" field in DB config!'
    assert d['dbms'] in get_args(supportedDialects), f'Unsupported "dbms" field value. Must be one of: {get_args(supportedDialects)}'
    user, password, host, port, database = get_keys(d, ('user', 'password', 'host', 'port', 'database'))
    assert isinstance(user, str), f'"user" field must be str! Got: {d["user"]}'
    assert isinstance(password, str), f'"password" field must be str! Got: {d["password"]}'
    assert isinstance(host, str), f'"host" field must by str! Got: {host}'
    assert isinstance(port, Optional[str]), f'"port" field must by str|None! Got: {port}'
    assert isinstance(database, str), f'"database" field must by str! Got: {database}'
    return WarehouserConfig(
        d['dbms'], # type: ignore
        database,
        user,
        password,
        host=host,
        port=port)
