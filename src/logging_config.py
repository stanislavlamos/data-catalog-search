import logging
import os
from logtail import LogtailHandler
from dotenv import load_dotenv


load_dotenv()
SOURCE_TOKEN = os.getenv("SOURCE_TOKEN")
INGEST_HOST = os.getenv("INGEST_HOST")

def get_logtail_logger(name: str, level=logging.INFO):
    """
    Returns a logger configured with Better Stack's Logtail handler.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if not any(isinstance(h, LogtailHandler) for h in logger.handlers):
        handler = LogtailHandler(source_token=SOURCE_TOKEN, host=INGEST_HOST)
        logger.addHandler(handler)

        # Optional: also log to console
        console = logging.StreamHandler()
        console.setLevel(level)
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        console.setFormatter(formatter)
        logger.addHandler(console)

    return logger
