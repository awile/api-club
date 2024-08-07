import os
from pydantic import BaseModel
from functools import lru_cache


class Settings(BaseModel):

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_NAME: str

    def get_db_connection_string(self, is_async: bool = True):
        format = "postgresql+asyncpg" if is_async else "postgresql"
        return f"{format}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:5432/{self.DB_NAME}"


@lru_cache
def init_settings() -> Settings:
    variables = {field: os.environ[field] for field in Settings.model_fields.keys()}
    return Settings(**variables)


def get_settings() -> Settings:
    return init_settings()
