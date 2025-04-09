import logging

logger = logging.getLogger("acp")


def configure_logger(*, log_level: int | None) -> None:
    uvicorn_logger = logging.getLogger("uvicorn")
    if len(uvicorn_logger.handlers) > 0:
        handler = uvicorn_logger.handlers[0]  # match formatting
        logger.addHandler(handler)

    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    if log_level is not None:
        logger.setLevel(log_level)
    elif uvicorn_error_logger.level != logging.NOTSET:
        handler = uvicorn_logger.handlers[0]
        logger.addHandler(handler)
        logger.setLevel(uvicorn_logger.level)
