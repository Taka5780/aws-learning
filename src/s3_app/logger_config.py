import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("awsapp")
    logger.setLevel(logging.INFO)

    formater = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_hender = TimedRotatingFileHandler(
        filename=LOG_DIR / "awsapp.log",
        when="D",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_hender.setFormatter(formater)

    if not logger.handlers:
        logger.addHandler(file_hender)

    return logger
