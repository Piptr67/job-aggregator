import logging
import sys

def setup_logger(log_level: str, name: str = "job_aggregator") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",    
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger