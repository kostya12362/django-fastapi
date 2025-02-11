import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Union

from loguru import logger

# from loguru._logger import Logger  # noqa


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen = "importlib" in filename and "_bootstrap" in filename
            if depth > 0 and not (is_logging or is_frozen):
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger(
    file_path: Optional[Path] = None,
    *,
    level: Union[str, int] = "INFO",
    log_format: str = "{time} {level} {message}",  # noqa
    rotation: str = "1 week",
    compression: str = "zip",
):
    """Configuration Loguru for integration with logging."""
    logger.remove()
    intercept_handler = InterceptHandler()
    if file_path:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        logger.add(
            file_path,
            format=log_format,
            level=level,
            rotation=rotation,
            compression=compression,
        )
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logging.root.handlers = [intercept_handler]
    logger.add(sys.stderr, format=log_format, level=level)

    # logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    # logger.remove()
    # logger.add(sys.stderr, format=log_format, filter=log_filter, level=level)
    #
    # # logger.remove()
    # intercept_handler = InterceptHandler()
    # if file_path:
    #     os.makedirs(os.path.dirname(file_path), exist_ok=True)
    #     logger.add(
    #         file_path,
    #         format=log_format,
    #         level=level,
    #         rotation=rotation,
    #         compression=compression,
    #     )
    # #
    # for name in logging.root.manager.loggerDict.keys():
    #     logging.getLogger(name).handlers = []
    #     logging.getLogger(name).propagate = True
    #
    # # logging.root.handlers = [intercept_handler]
    # logger.add(sys.stderr, format=log_format, level=level)
