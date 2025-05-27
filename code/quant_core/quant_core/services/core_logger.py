import logging
import os


LOG_COLORS = {
    logging.DEBUG: "\033[34m",  # Blue
    logging.INFO: "\033[32m",  # Green
    logging.WARNING: "\033[33m",  # Yellow
    logging.ERROR: "\033[31m",  # Red
    logging.CRITICAL: "\033[35m",  # Magenta
}

RESET_COLOR = "\033[0m"


class ColoredFormatter(logging.Formatter):
    """
    A custom formatter to add colors to log messages based on their level.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with color."""
        log_fmt = "%(asctime)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_fmt)
        original_message = formatter.format(record)

        color_code = LOG_COLORS.get(record.levelno, RESET_COLOR)
        colored_message = f"{color_code}{original_message}{RESET_COLOR}"

        return colored_message


class CoreLogger:
    """Singleton class for logging in the application."""

    _instance = None

    def __new__(cls) -> "CoreLogger":
        if cls._instance is None:
            cls._instance = super(CoreLogger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    @property
    def log_file_path(self) -> str:
        """Returns the log file path."""
        return os.getenv("LOG_FILE_PATH", f"{os.path.join(os.path.dirname(__name__), 'logs', 'app.log')}")

    def _initialize_logger(self) -> None:
        self._logger = logging.getLogger(  # type: ignore  # pylint: disable=attribute-defined-outside-init
            "core_logger"
        )
        log_level = os.getenv("LOG_LEVEL", "INFO")
        self._logger.setLevel(log_level)

        if not self._logger.hasHandlers():
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(ColoredFormatter())
            self._logger.addHandler(stream_handler)

            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)

            file_handler = logging.FileHandler(self.log_file_path, mode="a", encoding="utf-8")
            file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            self._logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """Returns the logger instance."""
        return self._logger

    def debug(self, message: str) -> None:
        """Logs a DEBUG message."""
        self._log(logging.DEBUG, message)

    def info(self, message: str) -> None:
        """Logs an INFO message."""
        self._log(logging.INFO, message)

    def warning(self, message: str) -> None:
        """Logs a WARNING message."""
        self._log(logging.WARNING, message)

    def error(self, message: str) -> None:
        """Logs an ERROR message."""
        self._log(logging.ERROR, message)

    def critical(self, message: str) -> None:
        """Logs a CRITICAL message."""
        self._log(logging.CRITICAL, message)

    def _log(self, level: int, message: str) -> None:
        """Handles logging."""
        self._logger.log(level, message)
