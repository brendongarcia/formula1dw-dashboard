import functools
import logging
import os
import time
from logging.handlers import RotatingFileHandler


def retry(max_attempts=3, backoff_seconds=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    logging.getLogger("etl").warning(
                        "Attempt %d/%d failed for %s: %s",
                        attempt, max_attempts, func.__name__, exc,
                    )
                    if attempt < max_attempts:
                        time.sleep(backoff_seconds * attempt)
            raise last_exc
        return wrapper
    return decorator


def setup_logging(log_dir, run_id, level=logging.INFO):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"etl_{run_id}.log")

    logger = logging.getLogger("etl")
    logger.setLevel(level)
    logger.handlers.clear()

    file_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(console_handler)

    return logger, log_path
