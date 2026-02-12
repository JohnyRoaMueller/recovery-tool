import tkinter as tk
import customtkinter as ctk
from customtkinter import CTkImage

from tkinter import filedialog

from typing import Optional, Any, List, Dict

import threading
import queue

from time import sleep

import re

from core.event_controller import EventController

from workers.monitor_worker import MonitorWorker
from workers.cmd_worker import CmdWorker
from workers.loading_worker import Loading_Worker
from workers.videoplayer import VideoPlayer

from ui.recoverStyles import STYLED_BUTTON
from ui.recoverStyles import WARNING_BUTTON
from ui.recoverStyles import BASE_CORNER_RADIUS
from ui.recoverStyles import BASE_PAD
from ui.recoverStyles import STYLED_DOT
from ui.recoverStyles import BACKGROUND_COLOR
from ui.recoverStyles import STYLED_LABEL

from core.enums.app_states import AppState
from core.enums.monitor_types import MonitorType

from core.mapper.status_mapper import download_mode_status_mapper, adb_status_mapper

import logging
logger = logging.getLogger(__name__)

class RecoveryApp:
    def __init__(self, root: tk.Tk) -> None:
        # Base
        self.root = root
        self.root.title("device_tool")
        self.root.geometry("640x420")
        self.root.minsize(640, 420)
        # Test on Hyprland
        self.root.maxsize(640, 420) 
        self.root.resizable(False, False) 
        # UI Buttons
        self.button_to_previous: tk.Button
        self.button_to_next: tk.Button

        # UI Labels
        self.header_label: tk.Label
        self.content_label_right: tk.Label
        self.content_label_left: tk.Label
        self.video_label: tk.Label

        # Threads
        self.events = EventController()
        self.q = queue.Queue()

        # Commands
        self.detect_download_mode = ['heimdall', 'detect']
        self.detect_device_bridge = ['adb', 'devices']
        self.flash_command = ["heimdall", "flash", "--RECOVERY", "../assets/twrp-3.5.2_9-1-i9300.img", "--no-reboot"]
        self.unlock_command = ['adb', 'shell', 'rm /data/system/password.key']

        # initialization
        self._build_ui()
        self.poll_queue()
        self.root.protocol("WM_DELETE_WINDOW", self.kill_threads)


    def _build_ui(self) -> None:
        ### FRAMES
        # Mainframe
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame. place(relx=0, rely=0, relwidth=1, relheight=1)
        # Headerframe
        self.header_frame = ctk.CTkFrame(self.main_frame) 
        self.header_frame.place(relx=0, rely=0, relwidth=1, relheight=0.2)
        # Contentframe
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.place(relx=0, rely=0.2, relwidth=1, relheight=0.6)
        # Grid Settings
        self.content_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="x")
        self.content_frame.grid_rowconfigure(0, weight=1)
        # Contentframe left
        self.content_frame_left = ctk.CTkFrame(self.content_frame, **BASE_CORNER_RADIUS)
        self.content_frame_left.grid(row=0, column=0, sticky="nsew", **BASE_PAD)
        # Contentframe center
        self.content_frame_center = ctk.CTkFrame(self.content_frame, **BASE_CORNER_RADIUS)
        self.content_frame_center.grid(row=0, column=1, sticky="nsew", **BASE_PAD)
        # Contentframe right
        self.content_frame_right = ctk.CTkFrame(self.content_frame, **BASE_CORNER_RADIUS)
        self.content_frame_right.grid(row=0, column=2, sticky="nsew", **BASE_PAD)
        # Footerframe
        self.footer_frame = ctk.CTkFrame(self.main_frame)
        self.footer_frame.place(relx=0, rely=0.8, relwidth=1, relheight=0.2)
        ### BUTTONS
        # Button center
        self.content_button_center = ctk.CTkButton(self.content_frame_center, **STYLED_BUTTON)
        # Button right
        self.content_button_right = ctk.CTkButton(self.content_frame_right, **STYLED_BUTTON)
        ### LABEL
        # USB detected information space
        self.header_label = ctk.CTkLabel(self.header_frame, text="", font=("Arial", 18, "bold"), text_color="black", fg_color="#505050", corner_radius=30)
        self.header_label.pack(expand=True, anchor="center", fill="x", **BASE_PAD)
        # Content space
        self.content_label_left = ctk.CTkLabel(self.content_frame_left, **STYLED_LABEL)
        # 
        self.content_label_center = ctk.CTkLabel(self.content_frame_center, **STYLED_LABEL)
        #
        self.content_label_center_video = ctk.CTkLabel(self.content_frame_center, **STYLED_LABEL)
        #
        self.content_label_right = ctk.CTkLabel(self.content_frame_right, **STYLED_LABEL)
        # content_label_list
        self.text_content_labels = [self.content_label_left, self.content_label_center, self.content_label_right]
        # Footer space
        self.loadingDots = []
        for _ in range(10):
            label = ctk.CTkLabel(self.footer_frame, **STYLED_DOT)
            label.pack(expand=True, side="left", fill="x", **BASE_PAD)
            self.loadingDots.append(label)
        # Video space
        self.video_label = ctk.CTkLabel(self.content_frame)
        # Start first page
        self.update_wraplength()
        self.changeState(AppState.INTRO)


    # set and remove items
    def setLabel(self, label: ctk.CTkLabel) -> None:
        label.pack(expand=True, anchor="center", fill="x", **BASE_PAD)
    def removeLabel(self, label: ctk.CTkLabel) -> None:
        label.pack_forget()
    def setButton(self, button: ctk.CTkButton) -> None:
        button.pack(side="bottom", expand=True, anchor="center", fill="x", **BASE_PAD)
    def removeButton(self, button: ctk.CTkButton) -> None:
        button.pack_forget()


    def changeState(self, state: AppState) -> None:
        self.state = state
        self.renderState(self.state)


    def renderState(self, state: AppState) -> None:
        match state:
            case AppState.INTRO:
                #
                self.setButton(self.content_button_center)
                self.setLabel(self.content_label_left)
                self.content_label_left.configure(text_color="lightgray", text="""
                                                            This tool is intended for personal data recovery on devices you own.
                                                        """)
                #
                self.setLabel(self.content_label_center)
                self.content_label_center.configure(text="""
                                                            Welcome to the GT-I9300 Recovery Tool.
                                                        """)
                #
                self.setLabel(self.content_label_right)
                self.content_label_right.configure(text_color="lightgray", text="""
                                                            All recovery actions are user-initiated and performed in officially accessible maintenance modes.
                                                        """)
                #
                self.content_button_center.configure(text="Start", command=lambda: self.changeState(AppState.FLASH_PREP))
                #
            case AppState.FLASH_PREP:
                #
                self.removeButton(self.content_button_center)
                self.removeLabel(self.content_label_center)
                self.removeLabel(self.content_label_left)
                self.removeLabel(self.content_label_right)
                #
                self.setLabel(self.content_label_center_video)
                #
                self.setLabel(self.content_label_left)
                self.content_label_left.configure(text_color="white", text="""
                                                                    1. Start Download Mode as shown in the video
                                                                    2. Connect your device via USB
                                                                    3. Press the FLASH button.
                                                                    """)
                #
                self.setButton(self.content_button_right)
                self.content_button_right.configure(text="FLASH", command=lambda: self.checkLoadOnCmd(self.flash_command), state="disabled")
                #
                self.download_mode_worker = MonitorWorker(self.q, self.events.stop_event_usb, MonitorType.DOWNLOAD_MODE, self.detect_download_mode, download_mode_status_mapper )
                self.download_mode_worker.start()
                #
                self.video_worker = VideoPlayer(self.q, self.events, self.content_frame)
                self.video_worker.start()
                #
            case AppState.FLASH_DONE:
                #
                self.events.stop_event_video.set()
                #
                self.removeLabel(self.header_label)
                self.removeLabel(self.content_label_left)
                self.removeLabel(self.content_label_center_video)
                #
                for dot in self.loadingDots:
                    dot.configure(fg_color="transparent")
                #
                self.setLabel(self.content_label_left)
                self.content_label_left.configure(text="The recovery image was flashed successfully.\nPlease turn off your Phone now.")
                #
                self.setLabel(self.content_label_center)
                self.content_label_center.configure(text="✔", font=("DejaVu Sans", 64), text_color="#2E7D32")
                #
                self.content_button_right.configure(text="Next Step", command=lambda: self.changeState(AppState.UNLOCK_PREP))
                self.content_button_right.configure(state="normal")
                #
            case AppState.UNLOCK_PREP:
                #
                self.events.stop_event_usb.set()
                self.events.stop_event_video.clear()
                self.events.video_switch_event.set()
                #
                self.removeLabel(self.content_label_center)
                #
                self.setLabel(self.header_label)
                self.setLabel(self.content_label_center_video)
                #
                self.video_worker = VideoPlayer(self.q, self.events, self.content_frame)
                self.video_worker.start()
                #
                for dot in self.loadingDots:
                    dot.configure(fg_color="#a1a1a1")
                #
                self.device_bridge_worker = MonitorWorker(self.q, self.events.stop_event_adb, MonitorType.DEVICE_BRIDGE, self.detect_device_bridge, adb_status_mapper )
                self.device_bridge_worker.start()
                #
                self.content_label_left.configure(text_color="white", text="""
                                                                    1. Start Recovery Mode as shown in the video
                                                                    2. Connect your device via USB
                                                                    3. Press the UNLOCK button.
                                                                    """)
                #
                self.content_button_right.configure(text="UNLOCK", command=lambda: self.checkLoadOnCmd(self.unlock_command), state="disabled" )
                #
            case AppState.UNLOCK_DONE:
                #
                self.events.stop_event_video.set()
                #
                self.removeLabel(self.header_label)
                self.removeLabel(self.content_label_center_video)
                #
                for dot in self.loadingDots:
                    dot.configure(fg_color="transparent")
                #
                self.content_label_left.configure(text="Screen lock successfully removed.\nYou can now use your phone again.")
                #
                self.setLabel(self.content_label_center)
                self.content_label_center.configure(text="🔓", font=("DejaVu Sans", 64), text_color="#2E7D32")
                #
                self.content_button_right.configure(text="CLOSE APP", command=self.kill_threads)
                self.content_button_right.configure(state="normal")
                #


    def updateUi(self, target: str, workerResult: Any) -> None:
            if target == 'header_label':
                self.header_label.configure(fg_color='red', text="Download Mode not detected") if workerResult.startswith('ERROR') else self.header_label.configure(fg_color='green', text="Download Mode detected")
                if not self.events.running_event_loading.is_set() and not self.events.stop_event_video.is_set():
                    self.content_button_right.configure(state="disabled", text_color="grey") if workerResult.startswith('ERROR') else self.content_button_right.configure(state="normal", text_color="white")

            if target == 'adb_detected_label':
                self.header_label.configure(fg_color='red', text="Adb not detected") if not bool(re.search(r'[1-9]', workerResult)) else self.header_label.configure(fg_color='green', text="Adb detected")
                if not self.events.running_event_loading.is_set() and not self.events.stop_event_video.is_set():
                    self.content_button_right.configure(state="disabled", text_color="grey") if not bool(re.search(r'[1-9]', workerResult)) else self.content_button_right.configure(state="normal", text_color="white")

            if target == 'videoplayer':
                if workerResult is not None:
                    if self.state not in (AppState.FLASH_PREP, AppState.UNLOCK_PREP):
                        return
                    imgtk = CTkImage(
                        light_image=workerResult["img"],
                        dark_image=workerResult["img"],
                        size=(workerResult["size_w"], workerResult["size_h"])
                    )
                    self.content_label_center_video.imgtk = imgtk
                    self.content_label_center_video.configure(image=imgtk)
                else:
                    self.content_label_center_video.imgtk = None
                    self.content_label_center_video.configure(image=None)


            if target == 'loading':
                color = "green" if workerResult == 0 else "red"
                self.root.after(0, self.update_loading_color, self.loadingDots, color)

    
    def tryAgainWarning(self, currentOperation: str) -> None:
        CONFIG = {**WARNING_BUTTON, "text": "TRY AGAIN"}
        self.content_button_right.configure(**CONFIG)

        self.root.after(3000, lambda: self.content_button_right.configure(
            **{**STYLED_BUTTON, "text": currentOperation}
        ))


    def update_loading_color(self, loadingDots, color, index=0):
        if index >= len(loadingDots):
            self.events.clearLoadingEvents()
            if color == "red":
                self.root.after(0, self.tryAgainWarning, "FLASH")
            else:
                self.root.after(0, lambda: self.changeState(
                    AppState.FLASH_DONE if self.state == AppState.FLASH_PREP else AppState.UNLOCK_DONE
                ))
            return

        loadingDots[index].configure(fg_color=color)
        self.root.after(100, self.update_loading_color, loadingDots, color, index + 1)


    def update_wraplength(self) -> None:
        for label in self.text_content_labels:
            label.configure(wraplength=label.winfo_width() - 20)
        self.root.after(100, self.update_wraplength)


    def cmd(self, q: queue.Queue, command: List[str], loading_stop_event: threading.Event) -> None:
        self.cmd_worker = CmdWorker(self.q, command, self.events)
        self.cmd_worker.start()


    def load(self, loadingDots: List[ctk.CTkLabel], loading_stop_event: threading.Event) -> None:
        self.content_button_right.configure(state="disabled")
        self.loading_worker = Loading_Worker(self.loadingDots, self.events)
        self.loading_worker.start()


    def checkLoadOnCmd(self, command: List[str]) -> None:
        self.cmd(self.q, command, self.events)
        self.load(self.loadingDots, self.events)


    def poll_queue(self) -> None:
        try:
            while True:
                queueContent = self.q.get_nowait()

                if queueContent.get('worker') == MonitorType.DOWNLOAD_MODE:
                    self.updateUi( 'header_label', queueContent.get('result') )
                    
                if queueContent.get('worker') == MonitorType.DEVICE_BRIDGE:
                    self.updateUi( 'adb_detected_label', queueContent.get('result') )

                if queueContent.get('worker') == 'VideoPlayer':
                    self.updateUi( 'videoplayer', queueContent.get('result') )

                if queueContent.get('worker') == 'CmdWorker':
                    self.updateUi( 'loading', queueContent.get('result') )
        except queue.Empty:
            pass
        except Exception:
            logger.exception("Unexpected error in poll_queue")
        finally:
            self.root.after(10, self.poll_queue)


    def kill_threads(self) -> None:
        self.events.stop_all()
        self.root.destroy()
        logger.info("window closed")
