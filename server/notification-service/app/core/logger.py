"""
Application logger module.
"""
from threading import Lock

from server_shared.logger import Logger
from server_shared.utils.meta_classes import Singleton

from app.core.config import config as app_config
from app.core.constants import SERVICE_NAME

class AppLogger(Logger, metaclass=Singleton):
    """
    Application logger that initializes with the service's Elasticsearch URL and name.
    """
    _init_lock = Lock()

    def __init__(self):
        with self._init_lock:
            if not hasattr(self, "_initialized"):
                es_url = app_config.ELASTICSEARCH_URL if app_config.ENABLE_ES_LOGGING else None
                super().__init__(
                    es_url=es_url,
                    service_name=SERVICE_NAME,
                    log_level="INFO"
                )
                self._initialized = True
                self.info(f"Logger initialized for service: {SERVICE_NAME}, Enabled ES Logging: {app_config.ENABLE_ES_LOGGING}")
logger = AppLogger()
