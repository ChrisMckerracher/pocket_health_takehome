from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker, scoped_session


class SessionFactory:
    """
    This session factory is use in order to manage scoped_sessions conveniently, rather than have my repositories
    directly depend on the sqlalchemy engine object
    """
    session_factory: sessionmaker

    def __init__(self, sql_engine: Engine):
        self.engine = sql_engine
        self.session_factory = sessionmaker(bind=sql_engine)

    def get(self) -> scoped_session:
        return scoped_session(self.session_factory)
