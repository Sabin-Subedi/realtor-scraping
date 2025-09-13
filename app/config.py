from pydantic_settings import BaseSettings


class Setting(BaseSettings):
    MONGO_URI: str
    WEBSHARE_ROTATING_PROXY_URL: str | None = None

    class Config:
        env_file = ".env"


settings = Setting()
