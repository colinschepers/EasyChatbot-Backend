
import logging
import logging.config
from flask import current_app as app


if "LOGGING_CONF_FILE" in app.config:
    logging.config.fileConfig(app.config["LOGGING_CONF_FILE"])

for logger_name, log_level in app.config["LOG_LEVELS"].items():
    logging.getLogger(logger_name).setLevel(log_level)

logger = logging.getLogger(app.config["LOGGER_NAME"])
