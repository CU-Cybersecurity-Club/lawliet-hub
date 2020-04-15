"""
Used to define configuration and logging options for the API server
"""

import uuid
import logging.config

"""
Configuration variables
"""

DEBUG = True
FLASK_ENV = "development"
SECRET_KEY = uuid.uuid4().hex

"""
Logging configuration
"""

logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] (%(levelname)s) %(module)s: %(message)s",
            },
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            },
            "logfile": {
                "class": "logging.FileHandler",
                "filename": "lawliet_hub.log",
                "formatter": "default",
                "level": "DEBUG",
            },
        },
        "root": {"level": "INFO", "handlers": ["wsgi", "logfile"]},
        "loggers": {
            "kubernetes": {
                "level": "DEBUG" if DEBUG else "INFO",
                "handlers": ["wsgi", "logfile"],
            }
        },
    }
)
