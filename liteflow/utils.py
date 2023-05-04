def make_class_event_aware(clazz):
    from .types import EventAware

    def add_event_listener(event_name, callback, options={}):
        if not isinstance(event_name, str):
            raise Exception("Events can only be added/removed from the class, not on individual objects.")
        EventAware.add_event_listener(clazz, event_name, callback, options)

    def remove_event_listener(event_name, callback=None, options={}):
        if not isinstance(event_name, str):
            raise Exception("Events can only be added/removed from the class, not on individual objects.")
        EventAware.remove_event_listener(clazz, event_name, callback, options)

    def dispatch_event(self, event_name, *args):
        EventAware.dispatch_event(self, event_name, *args)

    setattr(clazz, "event_listeners", {})
    setattr(clazz, "add_event_listener", add_event_listener)
    setattr(clazz, "remove_event_listener", remove_event_listener)
    setattr(clazz, "dispatch_event", dispatch_event)
