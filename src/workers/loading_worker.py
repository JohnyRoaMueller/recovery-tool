import threading

import subprocess

from time import sleep

import logging
from typing import List, Any

from core.event_controller import EventController

logger = logging.getLogger(__name__)

class Loading_Worker(threading.Thread):
    def __init__(self, loadingDots: List[ctk.CTkLabel], events: EventController) -> None:
        super().__init__()
        self.loadingDots = loadingDots
        self.stop_event_loading = events.stop_event_loading
        self.running_event_loading = events.running_event_loading

    def run(self) -> None:
        self.running_event_loading.set()
        for dot in self.loadingDots: # reset color of the dots before loading process
            dot.configure(fg_color='#a1a1a1') 
        while not self.stop_event_loading.is_set():
            for dot in self.loadingDots:
                if self.stop_event_loading.is_set(): break
                dot.configure(fg_color='white')
                sleep(0.01)
                dot.configure(fg_color='#a1a1a1')
                sleep(0.01)
            sleep(0.2)
