import logging
import logging.handlers
from contextvars import ContextVar
from pathlib import Path
from typing import Any

request_id_var: ContextVar[str] = ContextVar[str]('request_id', default='system')

_old_factory = logging.getLogRecordFactory()


def record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
    """Фабрика для создания LogRecord с добавлением request_id."""
    record = _old_factory(*args, **kwargs)
    if not hasattr(record, 'request_id'):
        record.request_id = request_id_var.get()
    return record


logging.setLogRecordFactory(record_factory)


def setup_logging(log_path: Path, level: int = logging.INFO) -> None:
    """Настраивает логирование FastAPI и Uvicorn."""
    app_fmt = '%(asctime)s -  %(levelname)s - [%(request_id)s] -  %(name)s: %(message)s'
    uvicorn_fmt = '%(asctime)s - %(levelname)s - %(name)s: %(message)s'
    log_path.parent.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(level)
    for h in list(root.handlers):
        root.removeHandler(h)
    fh = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,
        backupCount=1,
        encoding='utf-8',
    )
    fh.setFormatter(logging.Formatter(app_fmt))
    root.addHandler(fh)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(app_fmt))
    root.addHandler(stream_handler)
    uvicorn_formatter = logging.Formatter(uvicorn_fmt)
    for name in ('uvicorn', 'uvicorn.error', 'uvicorn.access', 'fastapi'):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        for h in list(logger.handlers):
            logger.removeHandler(h)
        sh = logging.StreamHandler()
        sh.setFormatter(uvicorn_formatter)
        logger.addHandler(sh)
        logger.propagate = False
