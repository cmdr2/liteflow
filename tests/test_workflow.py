from typing import Any
from liteflow import compile_workflow, Module
from liteflow.workflow import SequentialModule, ParallelModule, ConditionalModule, CallableWrapperModule

EVENT_RECORDINGS = []


def teardown_function():
    EVENT_RECORDINGS.clear()


def test_1_0_basics__none():
    assert compile_workflow(None) is None


def test_1_1_basics__illegal_type():
    class Foo:
        pass

    assert compile_workflow("foo") is None
    assert compile_workflow(42) is None
    assert compile_workflow(42.0) is None
    assert compile_workflow(True) is None
    assert compile_workflow(tuple()) is None
    assert compile_workflow(Foo()) is None
    assert compile_workflow(Foo) is None


def test_1_2_basics__empty_list():
    assert compile_workflow([]) is None


def test_1_3_basics__empty_set():
    assert compile_workflow(set()) is None


def test_1_4_basics__empty_dict():
    assert compile_workflow(dict()) is None


def test_1_5_basics__module_is_echoed_back():
    m = Module()
    assert compile_workflow(m) == m


def test_2_0_list__sequential_module_is_returned():
    workflow = [Module()]
    w = compile_workflow(workflow)

    assert isinstance(w, SequentialModule)


def test_2_1_list__internal_modules_are_linked_sequentially():
    workflow = [Module(), Module(), Module()]
    w = compile_workflow(workflow)

    add_listener(workflow[0], expect="a", emit="b")
    add_listener(workflow[1], expect="b", emit="c")
    add_listener(workflow[2], expect="c")

    w.dispatch_event("a")

    assert EVENT_RECORDINGS == ["a", "b", "c"]


def test_2_2_list__nested_list_receives_event_from_the_previous_module():
    workflow = [Module(), [Module(), Module()]]
    w = compile_workflow(workflow)

    add_listener(workflow[0], expect="a", emit="b")
    add_listener(workflow[1][0], expect="b", emit="c")
    add_listener(workflow[1][1], expect="c")

    w.dispatch_event("a")

    assert EVENT_RECORDINGS == ["a", "b", "c"]


def test_2_3_list__nested_list_joins_after_finishing_nesting():
    workflow = [Module(), [Module(), Module()], Module()]
    w = compile_workflow(workflow)

    add_listener(workflow[0], expect="a", emit="b")
    add_listener(workflow[1][0], expect="b", emit="c")
    add_listener(workflow[1][1], expect="c", emit="d")
    add_listener(workflow[2], expect="d")

    w.dispatch_event("a")

    assert EVENT_RECORDINGS == ["a", "b", "c", "d"]


def test_3_0_list__sequential_module_is_returned():
    workflow = {Module(), Module()}
    w = compile_workflow(workflow)

    assert isinstance(w, ParallelModule)


def test_3_1_set__internal_modules_are_linked_in_parallel():
    m1, m2, m3 = Module(), Module(), Module()
    workflow = {m1, m2, m3}
    w = compile_workflow(workflow)

    add_listener(m1, expect="a")
    add_listener(m2, expect="a")
    add_listener(m3, expect="a")

    w.dispatch_event("a")

    assert EVENT_RECORDINGS == ["a", "a", "a"]


def test_3_2_set__nested_set_receives_event_from_the_previous_module():
    m1, m2, m3 = Module(), Module(), Module()
    workflow = [m1, {m2, m3}]
    w = compile_workflow(workflow)

    add_listener(m1, expect="a", emit="b")
    add_listener(m2, expect="b")
    add_listener(m3, expect="b")

    w.dispatch_event("a")

    assert EVENT_RECORDINGS == ["a", "b", "b"]


def test_3_3_set__nested_set_joins_after_finishing_nesting():
    m1, m2, m3, m4 = Module(), Module(), Module(), Module()
    workflow = [m1, {m2, m3}, m4]
    w = compile_workflow(workflow)

    add_listener(m1, expect="a", emit="b")
    add_listener(m2, expect="b", emit="b1")
    add_listener(m3, expect="b", emit="b2")
    add_listener(m4, expect="b1")
    add_listener(m4, expect="b2")

    w.dispatch_event("a")

    # the set can be executed in any order
    assert EVENT_RECORDINGS == ["a", "b", "b", "b1", "b2"] or EVENT_RECORDINGS == ["a", "b", "b", "b2", "b1"]


def test_4_0_dict__conditional_module_is_returned():
    workflow = {"x": Module(), "y": Module()}
    w = compile_workflow(workflow)

    assert isinstance(w, ConditionalModule)


def test_4_1_dict__internal_modules_are_linked_conditionally():
    m1, m2 = Module(), Module()
    workflow = {"x": m1, "y": m2}
    w = compile_workflow(workflow)

    add_listener(m1, expect="x")
    add_listener(m2, expect="y")

    w.dispatch_event("x")
    assert EVENT_RECORDINGS == ["x"]

    EVENT_RECORDINGS.clear()

    w.dispatch_event("y")
    assert EVENT_RECORDINGS == ["y"]


def test_4_2_dict__nested_dict_receives_event_from_the_previous_module_conditionally():
    m1, m2, m3 = Module(), Module(), Module()
    workflow = [m1, {"x": m2, "y": m3}]
    w = compile_workflow(workflow)

    add_listener(m1, expect="a", emit="x")
    add_listener(m1, expect="b", emit="y")
    add_listener(m2, expect="x")
    add_listener(m3, expect="y")

    w.dispatch_event("a")
    assert EVENT_RECORDINGS == ["a", "x"]

    EVENT_RECORDINGS.clear()

    w.dispatch_event("b")
    assert EVENT_RECORDINGS == ["b", "y"]


def test_4_3_dict__nested_dict_joins_after_finishing_nesting():
    m1, m2, m3, m4 = Module(), Module(), Module(), Module()
    workflow = [m1, {"x": m2, "y": m3}, m4]
    w = compile_workflow(workflow)

    add_listener(m1, expect="a", emit="x")
    add_listener(m1, expect="b", emit="y")
    add_listener(m2, expect="x", emit="x1")
    add_listener(m3, expect="y", emit="y1")
    add_listener(m4, expect="x1")
    add_listener(m4, expect="y1")

    w.dispatch_event("a")
    assert EVENT_RECORDINGS == ["a", "x", "x1"]

    EVENT_RECORDINGS.clear()

    w.dispatch_event("b")
    assert EVENT_RECORDINGS == ["b", "y", "y1"]


def test_4_4_dict__keys_can_be_functions():
    is_upper = lambda event_name, *args: event_name.isupper()

    m1, m2 = Module(), Module()
    workflow = {"x": m1, is_upper: m2}
    w = compile_workflow(workflow)

    add_listener(m1, expect="x")
    add_listener(m2, expect="X")

    w.dispatch_event("x")
    assert EVENT_RECORDINGS == ["x"]

    EVENT_RECORDINGS.clear()

    w.dispatch_event("X")
    assert EVENT_RECORDINGS == ["X"]


def test_5_0_callable__callable_wrapper_module_is_returned():
    class M2:
        def __call__(self, *args: Any, **kwds: Any) -> Any:
            pass

    m1 = lambda: True
    m2 = M2()

    assert isinstance(compile_workflow(m1), CallableWrapperModule)
    assert isinstance(compile_workflow(m2), CallableWrapperModule)


def run_callable_test(task_create_fn):
    m1 = task_create_fn(emit="x1")
    m2a = task_create_fn(emit="x2a")
    m2b = task_create_fn(emit="x2b")
    m3 = task_create_fn()
    m4 = task_create_fn(emit="y1")
    m5 = task_create_fn()

    workflow = {
        "x": [m1, {m2a, m2b}, m3],
        "y": [m4, m5],
    }
    w = compile_workflow(workflow)

    w.dispatch_event("x")
    # the set can be executed in any order
    assert EVENT_RECORDINGS == ["x", "x1", "x1", "x2a", "x2b"] or EVENT_RECORDINGS == ["x", "x1", "x1", "x2b", "x2a"]

    EVENT_RECORDINGS.clear()

    w.dispatch_event("y")
    # the set can be executed in any order
    assert EVENT_RECORDINGS == ["y", "y1"]


def test_5_1_callable__workflow_tasks_can_be_functions():
    run_callable_test(task_create_fn=make_dummy_task_fn)


def test_5_2_callable__workflow_tasks_can_be_callable_objects():
    run_callable_test(task_create_fn=make_dummy_task_callable_object)


def test_5_3_callable__tasks_will_be_invoked_even_if_the_previous_task_returned_None():
    m1 = make_dummy_task_fn()
    m2 = make_dummy_task_callable_object()
    m3 = make_dummy_task_fn()

    workflow = [m1, m2, m3]
    w = compile_workflow(workflow)

    w.dispatch_event("x")

    assert EVENT_RECORDINGS == ["x", None, None]


def test_5_4_callable__task_functions_can_return_multiple_values():
    def task_a(a):
        EVENT_RECORDINGS.append(a)
        return "y", 42

    def task_b(a, b):
        EVENT_RECORDINGS.append([a, b])

    workflow = [task_a, task_b]
    w = compile_workflow(workflow)

    w.dispatch_event("x")

    assert ["x", ["y", 42]]


def make_dummy_task_fn(emit: str = None):
    def on_event(event_name: str, *args):
        EVENT_RECORDINGS.append(event_name)
        return emit

    return on_event


def make_dummy_task_callable_object(emit: str = None):
    class Foo:
        def __call__(self, event_name: str, *args: Any, **kwds: Any):
            EVENT_RECORDINGS.append(event_name)
            return emit

    return Foo()


def add_listener(m: Module, expect: str = None, emit: str = None):
    m.add_event_listener(expect, make_event(m, expect=expect, emit=emit))


def make_event(module: Module, expect: str = None, emit: str = None):
    def on_event(event_name: str):
        EVENT_RECORDINGS.append(event_name)
        if event_name == expect and emit:
            module.emit_event(emit)

    return on_event
