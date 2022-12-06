import os

from flask import Flask

from tbj_statsapp import DevelopmentConfig, ProductionConfig, TestingConfig


class ConfigException(Exception):
    """Exception raised for invalid configurations

    Attributes:
        message -- explanation of why config is invalid
    """

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


# Grab environment
environment = os.environ.get("FLASK_ENV", None)

if not environment:
    raise ConfigException("Environment is not defined")
elif environment.lower() == "development":
    config_settings = DevelopmentConfig()
elif environment.lower() == "testing":
    config_settings = TestingConfig()
elif environment.lower() == "production":
    config_settings = ProductionConfig()
else:
    raise ConfigException("Defined environment is invalid")


def create_app():
    """Create and initialize app according to the config"""
    app = Flask(__name__)
    app.config.from_object(config_settings)

    return app


if __name__ == "__main__":
    create_app().run()
