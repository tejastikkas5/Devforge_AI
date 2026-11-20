import queue
from typing import Callable, Any

class EventBus:
    """Thread-safe event queue for passing events from background threads to CustomTkinter main loop."""
    def __init__(self):
        self._queue = queue.Queue()

    def post(self, event_type: str, data: Any = None):
        """Called from worker threads to send events to UI."""
        self._queue.put((event_type, data))

    def poll(self, max_items: int = 50) -> list:
        """Called periodically by UI (via root.after) to process pending events."""
        events = []
        for _ in range(max_items):
            try:
                events.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return events

bus = EventBus()
