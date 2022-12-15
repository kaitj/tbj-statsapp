"""Configuration classes for Flask"""
import os

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    """Configuration class

    This class contains all global config variables needed for the app. Any
    sensitive variables, such as secret keys, should be set by the environment
    variable rather than explicitly stated here.
    """


class ProductionConfig(Config):
    """Config used in production app"""

    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")


class DevelopmentConfig(Config):
    """Config used in development of app"""

    DEBUG = True
    SECRET_KEY = "dev"


class TestingConfig(Config):
    """Config used for unit testing"""

    TESTING = True
    SECRET_KEY = "test"
