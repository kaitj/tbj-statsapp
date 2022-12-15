"""Instantiate Flask and set up plugins"""

import os
from datetime import timedelta

from flask import Flask

from flask_session import Session
from tbj_statsapp.config import (
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
)


class ConfigException(Exception):
    """Exception raised for invalid configurations

    Attributes:
        message -- explanation of why config is invalid
    """

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


# Grab environment
FLASK_ENV = os.environ.get("FLASK_ENV", False)
DEBUG = os.environ.get("FLASK_DEBUG", False)
TESTING = os.environ.get("FLASK_TESTING", False)

if DEBUG:
    config_settings = DevelopmentConfig()
elif TESTING:
    config_settings = TestingConfig()
elif not DEBUG and not TESTING:
    config_settings = ProductionConfig()
else:
    raise ConfigException("Improper environment configured")


def create_app():
    """Create and initialize app according to the config"""
    app = Flask(__name__)
    app.config.from_object(config_settings)

    # Cookie settings - same across all settings
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=6)

    Session(app)

    # Route views without Flask blueprints
    with app.app_context():
        from tbj_statsapp import views  # noqa: F401

    # Setup session

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
