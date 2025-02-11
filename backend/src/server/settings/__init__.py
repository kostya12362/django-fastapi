import importlib
from functools import lru_cache

from loguru import logger

from ._dantic import config as _config


@lru_cache(maxsize=1)
def init_config() -> None:
    pool = set()
    try:
        settings_module = importlib.import_module(f"server.settings.{_config.STATE}")
        logger.info(f"Using settings module: {settings_module.__name__}")
    except ModuleNotFoundError as e:
        raise ValueError(f"Unknown state '{_config.STATE}': {e}")

    for attr in dir(settings_module):
        if not attr.startswith("__"):
            globals()[attr] = getattr(settings_module, attr)
            pool.add(attr)

    for attr, value in _config.model_dump().items():
        globals()[attr] = getattr(_config, attr)
        if attr not in pool:
            pool.add(attr)
        else:
            logger.warning(f"Duplicate attribute '{attr}' found in settings modules")


init_config()
