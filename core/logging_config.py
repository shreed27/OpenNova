import logging
import os


def configure_logging():
    level_name = os.environ.get("JARVIS_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format="[%(levelname)s] %(name)s: %(message)s")
