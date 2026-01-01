from sqlalchemy import MetaData
from warehouser.core import make_warehouser
from warehouser.db_config import SqliteWhConfig, dbConfigDict
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from warehouser.manager import Warehouser

MTD = MetaData()

class Base(DeclarativeBase):
    metadata = MTD


class Tst(Base):
    __tablename__ = 'test_table'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str]
    
if __name__ == '__main__':
    # conf = SqliteWhConfig('test/Resources/test.db')
    conf: dbConfigDict = {
        'dialect': 'sqlite',
        'database': 'test/Resources/test.db'
    }
    # print(conf)
    # wh = Warehouser(conf, MTD, safe=False)
    wh = make_warehouser(conf, MTD)
    print(wh)
    
    data = [
        {'id': 1, 'value': 'test'},
        {'id': 2, 'value': 'test_test_2'}
    ]
    wh.upsert(Tst, data)