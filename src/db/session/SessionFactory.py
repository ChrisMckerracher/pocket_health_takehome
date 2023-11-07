from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, scoped_session


class SessionFactory:
    session_factory: sessionmaker

    def __init__(self, sql_engine: Engine):
        self.engine = sql_engine
        self.session_factory = sessionmaker(bind=sql_engine)

    def get(self) -> scoped_session:
        return scoped_session(self.session_factory)