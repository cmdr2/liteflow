from liteflow import EventAware, EventEmitter, Module

EVENT_RECORDINGS = []
EVENT_DATA = []


def teardown_function():
    EVENT_RECORDINGS.clear()
    EVENT_DATA.clear()


def test_1_0__register__can_register_event_listener():
    m = EventAware()
    m.add_event_listener("event_foo", dummy_event_listener)

    assert hasattr(m, "event_listeners")
    assert "event_foo" in m.event_listeners
    assert m.event_listeners["event_foo"][0] == (dummy_event_listener, {})


def test_1_1__register__can_register_event_listener_with_options():
    m = EventAware()
    m.add_event_listener("event_foo", dummy_event_listener, {"foo": 42})

    assert hasattr(m, "event_listeners")
    assert "event_foo" in m.event_listeners
    assert m.event_listeners["event_foo"][0] == (dummy_event_listener, {"foo": 42})


def test_1_2__register__can_remove_registered_event_listener_by_function():
    m = EventAware()
    m.add_event_listener("event_foo", dummy_event_listener)
    m.remove_event_listener("event_foo", dummy_event_listener)

    assert hasattr(m, "event_listeners")
    assert "event_foo" not in m.event_listeners


def test_1_3__register__can_remove_registered_event_listener_by_function__specific_listener_only():
    m = EventAware()
    m.add_event_listener("event_foo", dummy_event_listener)
    m.add_event_listener("event_foo", dummy_event_listener2)
    m.remove_event_listener("event_foo", dummy_event_listener)

    assert hasattr(m, "event_listeners")
    assert "event_foo" in m.event_listeners
    assert len(m.event_listeners["event_foo"]) == 1
    assert m.event_listeners["event_foo"][0][0] == dummy_event_listener2


def test_2_0__dispatch__can_invoke_registered_event_listener():
    m = EventAware()
    m.add_event_listener("event_foo", dummy_event_listener)

    m.dispatch_event("event_foo")

    assert EVENT_RECORDINGS == ["event_foo"]
    assert EVENT_DATA == [tuple()]


def test_2_1__dispatch__can_invoke_registered_event_listener_with_data():
    m = EventAware()
    m.add_event_listener("event_foo", dummy_event_listener)

    m.dispatch_event("event_foo", "hello", 42)

    assert EVENT_RECORDINGS == ["event_foo"]
    assert EVENT_DATA == [("hello", 42)]


def test_2_2__dispatch__can_invoke_registered_event_listener_multiple_times():
    m = EventAware()
    m.add_event_listener("event_foo", dummy_event_listener)

    m.dispatch_event("event_foo")
    m.dispatch_event("event_foo", "hello")
    m.dispatch_event("event_foo", 42)

    assert EVENT_RECORDINGS == ["event_foo", "event_foo", "event_foo"]
    assert EVENT_DATA == [tuple(), ("hello",), (42,)]


def test_2_3__dispatch__can_invoke_multiple_registered_event_listeners():
    m = EventAware()
    m.add_event_listener("event_foo", dummy_event_listener)
    m.add_event_listener("event_bar", dummy_event_listener)

    m.dispatch_event("event_foo", 42)
    m.dispatch_event("event_bar", "hello", 42)
    m.dispatch_event("event_foo")

    assert EVENT_RECORDINGS == ["event_foo", "event_bar", "event_foo"]
    assert EVENT_DATA == [(42,), ("hello", 42), tuple()]


def test_2_4__dispatch__can_specify_filtering_function_for_listeners():
    m = EventAware()
    m.add_event_listener("event_foo", dummy_event_listener, {"filter_fn": lambda event_name, *args: args[0] % 2 == 0})

    m.dispatch_event("event_foo", 42)
    assert EVENT_RECORDINGS == ["event_foo"]
    assert EVENT_DATA == [(42,)]

    EVENT_RECORDINGS.clear()
    EVENT_DATA.clear()

    m.dispatch_event("event_foo", 41)
    assert EVENT_RECORDINGS == []
    assert EVENT_DATA == []


def test_3_0__emitter__can_attach_output_module():
    a = EventEmitter()
    b = EventAware()
    a.attach_output_listener(b)

    assert hasattr(a, "output_listeners")
    assert b in a.output_listeners


def test_3_1__emitter__can_detach_output_module():
    a = EventEmitter()
    b = EventAware()
    a.attach_output_listener(b)
    a.detach_output_listener(b)

    assert hasattr(a, "output_listeners")
    assert b not in a.output_listeners


def test_3_1__emitter__can_emit_event_to_output_module():
    a = EventEmitter()
    b = EventAware()
    a.attach_output_listener(b)

    b.add_event_listener("event_foo", dummy_event_listener)

    a.emit_event("event_foo", 42)

    assert EVENT_RECORDINGS == ["event_foo"]
    assert EVENT_DATA == [(42,)]


def test_3_2__emitter__can_emit_event_to_multiple_output_modules():
    a = EventEmitter()
    b1 = EventAware()
    b2 = EventAware()
    a.attach_output_listener(b1)
    a.attach_output_listener(b2)

    b1.add_event_listener("event_foo", dummy_event_listener)
    b2.add_event_listener("event_foo", dummy_event_listener2)

    a.emit_event("event_foo", 42)

    assert EVENT_RECORDINGS == ["event_foo", "event_foo"]
    assert EVENT_DATA == [(42,), (42,)]


def test_3_2__emitter__can_emit_event_to_multiple_output_modules__different_events():
    a = EventEmitter()
    b1 = EventAware()
    b2 = EventAware()
    a.attach_output_listener(b1)
    a.attach_output_listener(b2)

    b1.add_event_listener("event_foo", dummy_event_listener)
    b2.add_event_listener("event_bar", dummy_event_listener2)

    a.emit_event("event_foo", 42)
    a.emit_event("event_bar", 420)

    assert EVENT_RECORDINGS == ["event_foo", "event_bar"]
    assert EVENT_DATA == [(42,), (420,)]


def test_4_0__module__is_eventaware_and_eventemitter():
    m = Module()
    assert isinstance(m, EventAware)
    assert isinstance(m, EventEmitter)


def test_4_1__module__event_handlers_can_be_external_functions():
    m = Module()

    def on_event(event_name: str):
        EVENT_RECORDINGS.append(event_name)

    m.add_event_listener("event_foo", on_event)
    m.dispatch_event("event_foo")

    assert EVENT_RECORDINGS == ["event_foo"]


def test_4_2__module__event_handlers_can_be_class_methods():
    class Foo(Module):
        def __init__(self) -> None:
            self.add_event_listener("event_foo", self.on_event)

        def on_event(self, event_name: str):
            EVENT_RECORDINGS.append(event_name)

    m = Foo()
    m.dispatch_event("event_foo")

    assert EVENT_RECORDINGS == ["event_foo"]


def dummy_event_listener(event_name: str, *args):
    EVENT_RECORDINGS.append(event_name)
    EVENT_DATA.append(args)


def dummy_event_listener2(event_name: str, *args):
    EVENT_RECORDINGS.append(event_name)
    EVENT_DATA.append(args)
