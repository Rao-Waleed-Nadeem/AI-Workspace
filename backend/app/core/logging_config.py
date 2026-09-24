import logging

from app.core.config import settings


class SecretRedactionFilter(logging.Filter):
    """Prevent common secret-like fields from appearing in log messages."""

    SENSITIVE_NAMES = (
        "api_key",
        "password",
        "token",
        "authorization",
        "secret",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        lowered = message.lower()

        if any(name in lowered for name in self.SENSITIVE_NAMES):
            record.msg = "Sensitive log message suppressed."
            record.args = ()

        return True


def configure_logging() -> None:
    level = getattr(
        logging,
        settings.LOG_LEVEL.upper(),
        logging.INFO,
    )

    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        force=True,
    )

    for handler in logging.getLogger().handlers:
        handler.addFilter(
            SecretRedactionFilter()
        )