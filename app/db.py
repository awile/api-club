from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from .settings import get_settings
from functools import lru_cache


@lru_cache
def session_factory() -> async_sessionmaker[AsyncSession]:
    settings = get_settings()
    uri = settings.get_db_connection_string()
    engine = create_async_engine(uri, pool_pre_ping=True)
    return async_sessionmaker(
        autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
    )


def get_session(request: Request) -> AsyncSession:
    if not hasattr(request.state, "session") or request.state.session is None:
        session = session_factory()()
        request.state.session = session
    return request.state.session


async def get_db_session(request: Request) -> AsyncSession:
    return get_session(request)
