import threading

import subprocess

from time import sleep

from queue import Queue
from core.event_controller import EventController

from core.app_logging import log_subprocess
import logging
logger = logging.getLogger(__name__)


class CmdWorker(threading.Thread):
    def __init__(self, queue: Queue, command: list[str], events: EventController):
        super().__init__()
        self.queue = queue
        self.command = command
        self.stop_event_loading = events.stop_event_loading
        
    def run(self):
        try:
            self.proc = subprocess.run(
                self.command,
                capture_output=True,
                text=True,
                check=False,
                timeout=5000
            )
            log_subprocess(self.proc.returncode, self.proc.stderr, logger)
            self.queue.put({"worker": "CmdWorker", "result": self.proc.returncode})
        except subprocess.SubprocessError:
            logger.exception("Subprocess execution failed")
            self.queue.put({"worker": "CmdWorker", "result": -1})
            
        self.stop_event_loading.set()