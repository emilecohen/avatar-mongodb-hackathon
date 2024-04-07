import os
from pathlib import Path

from pydantic import Extra
from pydantic_settings import BaseSettings

from dotenv import load_dotenv

DEV_ENV = "development"
STAGING_ENV = "staging"
PRODUCTION_ENV = "production"
TEST_ENV = "test"

ENV = os.getenv("ENV")
env_path = Path(__file__).parent.parent.parent / "dotenv"

if ENV in [PRODUCTION_ENV, STAGING_ENV]:
    env_path /= ".env"
elif ENV == DEV_ENV:
    env_path /= "dev.env"
elif ENV == TEST_ENV:
    env_path /= "test.env"
else:
    raise ValueError(f"ENV value {ENV} not supported")

print("env_path", env_path)
DEBUG = ENV == DEV_ENV


class Settings(BaseSettings):
    load_dotenv(dotenv_path=env_path)

    OPEN_AI_KEY: str | None = os.getenv("OPEN_AI_KEY")
    MONGODB_PASSWORD: str | None = os.getenv("MONGODB_PASSWORD")

    class Config:
        env_file = ".env"
        extra = Extra.allow


settings = Settings()
