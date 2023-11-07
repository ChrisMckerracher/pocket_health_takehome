from sqlalchemy.orm import scoped_session

from src.db.session.SessionFactory import SessionFactory


class CtxSession:
    ctx_session: SessionFactory = None

    @staticmethod
    def get() -> scoped_session:
        return CtxSession.ctx_session.get()

    @staticmethod
    def set(factory: SessionFactory):
        CtxSession.ctx_session = factory


ctx_session = CtxSession
