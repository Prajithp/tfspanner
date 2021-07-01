from celery import Celery
from config.settings import settings
from celery.signals import after_setup_task_logger, after_setup_logger
from celery.app.log import TaskFormatter
from utils.logger import CELERY_LOG_FORMAT


class Config:
    broker_url = "sqla+" + settings.SQLALCHEMY_DATABASE_URI
    include = ["tasks.module"]


celery_app = Celery("TerraSpanner")
celery_app.config_from_object(Config())
celery_app.connection().ensure_connection(max_retries=3, timeout=15)


@after_setup_logger.connect
@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(TaskFormatter(CELERY_LOG_FORMAT))
