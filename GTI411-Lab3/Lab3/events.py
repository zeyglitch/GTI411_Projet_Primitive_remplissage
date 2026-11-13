


class EventManager:
    def __init__(self) -> None:
        self._events = {}
    
    def register(self, event_name:str, func):
        if event_name not in self._events:
            self._events[event_name] = []
        self._events[event_name].append(func)

    def trigger(self, event_name:str, *args, **kwargs):
        if event_name in self._events:
            for func in self._events[event_name]:
                func(*args, **kwargs)


event_manager = EventManager()