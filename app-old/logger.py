
import logging
import logging.config
from config import config

if "LOGGING_CONF_FILE" in config:
    logging.config.fileConfig(config["LOGGING_CONF_FILE"])

for logger_name, log_level in config["LOG_LEVELS"].items():
    logging.getLogger(logger_name).setLevel(log_level)

logger = logging.getLogger(config["LOGGER_NAME"])
