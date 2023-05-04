from liteflow.utils import make_class_event_aware


def test_1_0__make_class_event_aware():
    class Foo:
        def foo():
            pass

    make_class_event_aware(Foo)

    assert hasattr(Foo, "event_listeners") and Foo.event_listeners == {}
    assert hasattr(Foo, "add_event_listener") and callable(Foo.add_event_listener)
    assert hasattr(Foo, "remove_event_listener") and callable(Foo.remove_event_listener)
    assert hasattr(Foo, "add_event_listener") and callable(Foo.dispatch_event)


def test_1_1__patched_class_registers_and_receives_events():
    class Foo:
        def foo():
            pass

    make_class_event_aware(Foo)

    called = False

    def on_event(event_name: str):
        nonlocal called
        called = event_name == "event_foo"

    Foo.add_event_listener("event_foo", on_event)

    f = Foo()
    f.dispatch_event("event_foo")

    assert called


def test_1_2__cannot_add_or_remove_listeners_on_class_instance():
    class Foo:
        def foo():
            pass

    make_class_event_aware(Foo)

    f = Foo()
    try:
        f.add_event_listener("event_foo", lambda event_name, *args: True)
    except:
        return

    try:
        f.remove_event_listener("event_foo")
    except:
        return

    assert False
