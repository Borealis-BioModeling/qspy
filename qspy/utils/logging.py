import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import functools
import time
import pprint

LOGGER_NAME = "qspy"
LOG_PATH = ".qspy/logs/qspy.log"


def setup_qspy_logger(
    log_path=LOG_PATH, max_bytes=1_000_000, backup_count=5, level=logging.INFO
):
    log_file = Path(log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)

    if not logger.hasHandlers():  # Prevent duplicate handlers on reload
        logger.addHandler(handler)

    logger.info("QSPy logging initialized.")
    return logger


_LOGGER_INITIALIZED = False


def ensure_qspy_logging():
    global _LOGGER_INITIALIZED
    if not _LOGGER_INITIALIZED:
        setup_qspy_logger()
        _LOGGER_INITIALIZED = True


def log_event(
    logger_name=LOGGER_NAME, log_args=False, log_result=False, static_method=False
):
    ensure_qspy_logging()
    logger = logging.getLogger(logger_name)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if static_method:
                args = args[1:]
            fname = func.__qualname__
            logger.info(f">>> Entering `{fname}`")
            if log_args:
                logger.info(f"    Args: {args}, Kwargs: {kwargs}")
            start = time.time()
            print(args, kwargs)
            result = func(*args, **kwargs)

            duration = time.time() - start
            logger.info(f"<<< Exiting `{fname}` ({duration:.3f}s)")
            if log_result:
                logger.info(f"    Result: {result}")
            return result

        return wrapper

    return decorator


REDACT_KEYS = {"current_user", "author", "hostname", "ip", "email"}


def redact_sensitive(data):
    if isinstance(data, dict):
        return {
            k: "[REDACTED]" if k in REDACT_KEYS else redact_sensitive(v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [redact_sensitive(i) for i in data]
    return data


def log_model_metadata(
    metadata, logger_name=LOGGER_NAME, level=logging.INFO, redact=True
):
    """
    Log QSPy model metadata in structured format, with optional redaction.

    Args:
        metadata (dict): The metadata dictionary to log.
        logger_name (str): Name of the logger.
        level (int): Logging level.
        redact (bool): If True, redact sensitive fields.
    """
    logger = logging.getLogger(logger_name)
    if not metadata:
        logger.warning("No metadata provided to log.")
        return

    header = "QSPy metadata snapshot"
    if redact:
        metadata = redact_sensitive(metadata)
        header += " (sensitive fields redacted)"
    logger.log(level, header + ":")

    for line in pprint.pformat(metadata, indent=2).splitlines():
        logger.log(level, f"    {line}")


def log_context_entry_exit(logger_name=LOGGER_NAME, log_duration=True, track_attr=None):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            logger = logging.getLogger(logger_name)
            context_name = getattr(self, "name", self.__class__.__name__)
            is_enter = method.__name__ == "__enter__"
            is_exit = method.__name__ == "__exit__"

            if is_enter:
                self._qspy_context_start = time.time()
                self._qspy_pre_ids = set()
                if track_attr:
                    tracked = getattr(self.model, track_attr, [])
                    self._qspy_pre_ids = set(id(x) for x in tracked)
                logger.info(f">>> Entering context: `{context_name}`")

            result = method(self, *args, **kwargs)

            if is_exit:
                duration = ""
                if log_duration and hasattr(self, "_qspy_context_start"):
                    elapsed = time.time() - self._qspy_context_start
                    duration = f" (duration: {elapsed:.3f}s)"
                logger.info(f"<<< Exiting context: `{context_name}`{duration}")

                if track_attr:
                    tracked = getattr(self.model, track_attr, [])
                    added = [x for x in tracked if id(x) not in self._qspy_pre_ids]
                    logger.info(f"    ↳ Added {len(added)} new `{track_attr}`:")
                    for obj in added:
                        logger.info(f"       - {getattr(obj, 'name', repr(obj))}")

            return result

        return wrapper

    return decorator
