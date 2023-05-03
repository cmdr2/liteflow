def make_class_event_aware(clazz):
    from .types import EventAware

    def add_event_listener(event_name, callback, options={}):
        if not isinstance(event_name, str):
            raise Exception("Events can only be added/removed from the class, not on individual objects.")
        EventAware.add_event_listener(clazz, event_name, callback, options)

    def remove_event_listener(event_name, callback, options={}):
        if not isinstance(event_name, str):
            raise Exception("Events can only be added/removed from the class, not on individual objects.")
        EventAware.remove_event_listener(clazz, event_name, callback, options)

    def _dispatch_event(self, event_name, use_capture, event):
        args = (self,) + args
        EventAware._dispatch_event(self, event_name, use_capture, event)

    setattr(clazz, "event_listeners", {})
    setattr(clazz, "add_event_listener", add_event_listener)
    setattr(clazz, "remove_event_listener", remove_event_listener)
    setattr(clazz, "dispatch_event", EventAware.dispatch_event)
    setattr(clazz, "dispatch_capture_event", EventAware.dispatch_capture_event)
    setattr(clazz, "_dispatch_event", _dispatch_event)
