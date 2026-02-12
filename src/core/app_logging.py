import threading

import logging

from time import perf_counter

from pathlib import Path

def setup_logging(log_dir: Path) -> None:
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

def log_subprocess(returncode: int, stderr: str, logger: logging.Logger) -> None:
    if returncode != 0:
        logger.error("Subprocess failed (rc=%s)", returncode)
        if stderr:
            logger.error("stderr:%s", stderr.strip())
    else:
        logger.info("Subprocess completed successfully")