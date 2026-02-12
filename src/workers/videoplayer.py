import threading

import subprocess

from time import sleep

from customtkinter import CTkImage

from PIL import Image
import cv2

import logging
import queue
import tkinter as tk
from typing import Any, Dict

from pathlib import Path

from core.event_controller import EventController

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = ROOT_DIR / "assets"

class VideoPlayer(threading.Thread):
    def __init__(self, queue: queue.Queue, events: EventController, root: tk.Tk) -> None:
        super().__init__()
        self.queue = queue
        self.stop_event_video = events.stop_event_video
        self.video_switch_event = events.video_switch_event
        self.root = root
        self.srcs = {
            "firstVideo": str(ASSETS_DIR / "start_download_mode.mp4"),
            "secondVideo": str(ASSETS_DIR / "start_recovery_mode.mp4"),
        }
        self.cap: cv2.VideoCapture = cv2.VideoCapture(self.srcs["firstVideo"]) 

        print(self.srcs["firstVideo"])

    def run(self) -> None:
        logger.info("Videoworker started")
        while not self.stop_event_video.is_set():
            if self.video_switch_event.is_set():
                self.cap.release()
                self.cap = cv2.VideoCapture(self.srcs["secondVideo"]) 
                self.video_switch_event.clear()
                logger.info("Next Video selected")

            ret: bool
            frame: Any
            ret, frame = self.cap.read()
            if ret:
                # BGR → RGB (OpenCV use BGR)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # OpenCV → PIL Image
                img: Image.Image = Image.fromarray(frame)

                # Size of the Application Frame
                frame_width: int = self.root.winfo_width()
                frame_height: float = self.root.winfo_height() * 0.8

                # Keep the aspect ratio
                h_frame: int
                w_frame: int
                h_frame, w_frame = frame.shape[:2]
                scale: float = min(frame_width / w_frame, frame_height / h_frame)
                new_w: int = int(w_frame * scale)
                new_h: int = int(h_frame * scale)

                # Scale image
                img = img.resize((new_w, new_h), Image.LANCZOS)

                # Keep a reference, otherwise it will flicker
                self.queue.put({
                    "worker": "VideoPlayer",
                    "result": {"img": img, "size_w": new_w, "size_h": new_h}
                })
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # Thread end → GUI have to remove the Frame
        self.queue.put({
            "worker": "VideoPlayer",
            "result": None
        })
        self.cap.release()
        logger.info("Videoworker stopped")
