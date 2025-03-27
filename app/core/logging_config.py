"""Logging configuration for the application."""

import logging.config
import sys
from typing import Dict, Any

def configure_logging(environment: str = "development") -> None:
    """Configure logging for the application.
    
    Args:
        environment: Current environment (development/production)
    """
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default" if environment == "development" else "json",
                "level": "DEBUG" if environment == "development" else "INFO",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/mindbeat.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "json",
                "level": "INFO",
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console"],
                "level": "DEBUG" if environment == "development" else "INFO",
            },
            "app": {
                "handlers": ["console", "file"] if environment == "production" else ["console"],
                "level": "DEBUG" if environment == "development" else "INFO",
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
    
    logging.config.dictConfig(config)
