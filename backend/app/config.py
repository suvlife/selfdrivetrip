"""Application configuration using pydantic-settings."""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://selfdrivetrip:password@postgres:5432/selfdrivetrip"

    # AI / LLM
    AI_API_KEY: str = ""
    AI_API_BASE_URL: str = "https://api.learnclub.ai/v1"
    AI_MODEL: str = "deepseek-chat"

    # Amap (高德地图)
    AMAP_KEY: str = ""

    # Unsplash
    UNSPLASH_ACCESS_KEY: str = ""

    # OpenWeatherMap
    OPENWEATHERMAP_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,https://go.suv.life"

    # App
    APP_NAME: str = "SelfDriveTrip"
    DEBUG: bool = False

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
