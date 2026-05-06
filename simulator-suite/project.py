"""
Application configuration.
Reads environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "simulator-suite-secret-key-2024")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # Simulation limits
    MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "100"))
    MAX_FRAMES = int(os.getenv("MAX_FRAMES", "20"))
    MIN_FRAMES = 1

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
