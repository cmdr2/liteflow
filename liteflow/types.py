from __future__ import annotations

import traceback


class EventAware:
    def add_event_listener(self, event_name: str, callback, options={}):
        if not hasattr(self, "event_listeners"):
            setattr(self, "event_listeners", {})

        event_listeners = getattr(self, "event_listeners")
        event_listeners[event_name] = event_listeners.get(event_name, [])
        event_listeners[event_name].append((callback, options))

    def remove_event_listener(self, event_name: str, callback=None, options={}):
        if not hasattr(self, "event_listeners"):
            setattr(self, "event_listeners", {})

        event_listeners = getattr(self, "event_listeners")
        if event_name not in event_listeners:
            return

        listeners = event_listeners[event_name]

        if callback:
            idx = -1
            for i, (l, opts) in enumerate(listeners):
                if l == callback:
                    idx = i
                    break

            if idx != -1:
                del listeners[idx]

        if len(listeners) == 0 or callback is None:
            del event_listeners[event_name]

    def dispatch_event(self, event_name: str, *args):
        if not hasattr(self, "event_listeners"):
            setattr(self, "event_listeners", {})

        event_listeners = getattr(self, "event_listeners")
        event_listeners = event_listeners.get(event_name, []) + event_listeners.get("*", [])
        for listener, opts in event_listeners:
            try:
                if "filter_fn" in opts and not opts["filter_fn"](event_name, *args):
                    continue
            except:
                print(
                    f"WARN: Error while running the filter function for event: {event_name}",
                    traceback.format_exc(),
                )
                continue

            listener(event_name, *args)


class EventEmitter:
    def attach_output_listener(self, listener):
        if not hasattr(self, "output_listeners"):
            setattr(self, "output_listeners", [])
        self.output_listeners.append(listener)

    def detach_output_listener(self, listener):
        if not hasattr(self, "output_listeners"):
            setattr(self, "output_listeners", [])
        self.output_listeners.remove(listener)

    def emit_event(self, event_name: str, *args):
        if not hasattr(self, "output_listeners"):
            return
        output_listeners = list(filter(lambda x: getattr(x, "enabled", True), self.output_listeners))
        for output_listener in output_listeners:
            output_listener.dispatch_event(event_name, *args)


class Module(EventAware, EventEmitter):
    pass
