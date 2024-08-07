import os
from pydantic import BaseModel
from functools import lru_cache


class Settings(BaseModel):

    DB_FILE_PATH: str

    def get_db_connection_string(self, is_async: bool = True):
        format = "sqlite+aiosqlite" if is_async else "sqlite"
        return f"{format}://{self.DB_FILE_PATH}"


@lru_cache
def init_settings() -> Settings:
    variables = {field: os.environ[field] for field in Settings.model_fields.keys()}
    return Settings(**variables)


def get_settings() -> Settings:
    return init_settings()
