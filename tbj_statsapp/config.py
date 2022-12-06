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


class DevelopmentConfig(Config):
    """Config used in development of app"""

    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    """Config used for unit testing"""

    DEBUG = True
    TESTING = True
