"""Opt-in, structured diagnostics for TradeTide workflows."""

import logging

LOGGER_NAME = "TradeTide"
logger = logging.getLogger(LOGGER_NAME)
logger.addHandler(logging.NullHandler())


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure concise console logging and return TradeTide's logger."""
    logger.setLevel(level)
    logger.propagate = False
    if not any(
        getattr(handler, "_tradetide_handler", False) for handler in logger.handlers
    ):
        handler = logging.StreamHandler()
        handler._tradetide_handler = True  # type: ignore[attr-defined]
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s: %(message)s", "%H:%M:%S"
            )
        )
        logger.addHandler(handler)
    return logger


def enable_debug_logging() -> logging.Logger:
    """Enable Python DEBUG logs and native debug output for new objects."""
    import TradeTide

    TradeTide.debug_mode = True
    return configure_logging(logging.DEBUG)


def disable_debug_logging() -> None:
    """Disable native debug output for subsequently created TradeTide objects."""
    import TradeTide

    TradeTide.debug_mode = False
    logger.setLevel(logging.WARNING)
