from celery import Celery
from celery_once import QueueOnce
from config.settings import settings
from celery.signals import after_setup_task_logger, after_setup_logger, worker_ready
from celery_singleton import clear_locks
from celery.app.log import TaskFormatter
from utils.logger import CELERY_LOG_FORMAT


class Config:
    broker_url = "sqla+" + settings.SQLALCHEMY_DATABASE_URI

    include = ["tasks.module", "tasks.tfrunner"]
    singleton_backend_url = settings.CELERY_REDIS_URI
    singleton_raise_on_duplicate = True
    singleton_lock_expiry = 60 * 60 * 2
    worker_hijack_root_logger = False
    worker_redirect_stdouts = False


celery_app = Celery("TerraSpanner")
celery_app.config_from_object(Config())
celery_app.connection().ensure_connection(max_retries=3, timeout=15)


@after_setup_logger.connect
@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(TaskFormatter(CELERY_LOG_FORMAT))


@worker_ready.connect
def unlock_all(**kwargs):
    clear_locks(celery_app)
