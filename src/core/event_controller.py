import threading


class EventController:
    def __init__(self) -> None:
        self.stop_event_usb: threading.Event = threading.Event()

        self.stop_event_adb: threading.Event = threading.Event()

        self.stop_event_loading: threading.Event = threading.Event()
        self.running_event_loading: threading.Event = threading.Event()

        self.stop_event_video: threading.Event = threading.Event()
        self.video_switch_event: threading.Event = threading.Event()

    def setEvent(self, event: threading.Event) -> None:
        event.set()

    def clearLoadingEvents(self) -> None:
        self.stop_event_loading.clear()
        self.running_event_loading.clear()

    def stop_all(self) -> None:
        self.stop_event_usb.set()
        self.stop_event_adb.set()
        self.stop_event_loading.set()
        self.stop_event_video.set()
        self.video_switch_event.set()
