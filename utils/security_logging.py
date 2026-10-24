import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path

from utils.paths import get_user_data_dir

_LOGGER_NAME = "student_management_system.security"
_SECRET_PATTERN = re.compile(
    r"(?i)(password|passphrase|api[_-]?key|secret|token|address|phone|image|photo)\s*=\s*[^\s,;]+"
)


def _redact(message: str) -> str:
    return _SECRET_PATTERN.sub(lambda match: f"{match.group(1)}=[REDACTED]", message)


class RedactingFormatter(logging.Formatter):
    def format(self, record):
        return _redact(super().format(record))


def get_security_logger() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger

    log_dir = Path(get_user_data_dir()) / "StudentManagementSystem" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        log_dir / "security.log",
        maxBytes=2 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(
        RedactingFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def log_security_event(message: str, level=logging.INFO, exc_info=False):
    get_security_logger().log(level, _redact(message), exc_info=exc_info)
