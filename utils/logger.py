import logging
import logging.handlers

CELERY_LOG_FORMAT = (
    "[%(asctime)s] [%(levelname)s] [%(task_name)s] [%(task_id)s] %(message)s"
)
LOG_FORMAT = (
    "[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s:%(lineno)s] %(message)s"
)


def getLogger(name):
    logger = logging.getLogger(name)
    default_formatter = logging.Formatter(LOG_FORMAT)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(default_formatter)

    logger.addHandler(console_handler)

    return logger
