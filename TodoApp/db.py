from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:test1234!@127.0.0.1:3306/ToDoApplication'


# def _fk_pragma_on_connect(dbapi_con, con_record):
#     dbapi_con.execute('pragma foreign_keys=ON')


engine = create_engine(SQLALCHEMY_DATABASE_URL)
# event.listen(engine, 'connect', _fk_pragma_on_connect)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
