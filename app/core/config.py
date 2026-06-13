from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Maintenance Fund Allocation CDSS"
    app_env: str = "development"
    debug: bool = False

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "cdss_user"
    mysql_password: str = Field(default="change_me", repr=False)
    mysql_database: str = "maintenance_cdss"

    jwt_secret_key: str = Field(default="change-this-to-a-long-random-secret", repr=False)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
