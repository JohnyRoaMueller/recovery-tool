import threading

import subprocess

from time import sleep

import logging
logger = logging.getLogger(__name__)


class MonitorWorker(threading.Thread):
    def __init__(self, queue: queue.Queue, event: threading.Thread, monitor_type: MonitorType, command: list[str], status_mapper: Callable[[str], Any] ) -> None:
        super().__init__()
        self.queue = queue
        self.command = command
        self.stop_event = event
        self.monitor_type = monitor_type
        self.status_mapper = status_mapper
        self.spResult: str
        self.result: str
        self.last_result: str

    def run(self) -> None:
        logger.info("%s monitor started", self.monitor_type.name)
        self.last_result = ""
        while not self.stop_event.is_set():
            try:
                self.spResult = subprocess.run(                        
                    self.command,
                    capture_output=True,
                    text=True,
                    check=True
                )  
                self.result = self.spResult.stdout
            except subprocess.CalledProcessError as e:
                self.result = e.stderr

            if self.result != self.last_result:
                readable_status = self.status_mapper(self.result)

                logger.info("%s status changed to %s",self.monitor_type.name, readable_status)

                self.last_result = self.result
            sleep(0.1)
            self.queue.put({"worker": self.monitor_type, "result": self.result})

