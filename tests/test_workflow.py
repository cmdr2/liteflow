from liteflow import compile_workflow, Module
from liteflow.workflow import SequentialModule, ParallelModule, ConditionalModule

EVENT_RECORDINGS = []


def teardown_function():
    EVENT_RECORDINGS.clear()


def test_1_0_basics__none():
    assert compile_workflow(None) is None


def test_1_1_basics__illegal_type():
    assert compile_workflow("foo") is None
    assert compile_workflow(42) is None
    assert compile_workflow(42.0) is None
    assert compile_workflow(True) is None
    assert compile_workflow(tuple()) is None


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


def test_2_3_list__nested_list_joins_after_finishing_nesting__NOT_IMPLEMENTED():
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


def test_3_3_set__nested_set_joins_after_finishing_nesting__NOT_IMPLEMENTED():
    m1, m2, m3, m4 = Module(), Module(), Module(), Module()
    workflow = [m1, {m2, m3}, m4]
    w = compile_workflow(workflow)

    add_listener(m1, expect="a", emit="b")
    add_listener(m2, expect="b", emit="b1")
    add_listener(m3, expect="b", emit="b2")
    add_listener(m4, expect="b1")
    add_listener(m4, expect="b2")

    w.dispatch_event("a")

    assert EVENT_RECORDINGS == ["a", "b", "b1", "b", "b2"]


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


def test_4_3_dict__nested_dict_joins_after_finishing_nesting__NOT_IMPLEMENTED():
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


def add_listener(m: Module, expect: str = None, emit: str = None):
    m.add_event_listener(expect, make_event(expect=expect, emit=emit))


def make_event(expect: str = None, emit: str = None):
    def on_event(self, event_name: str):
        EVENT_RECORDINGS.append(event_name)
        if event_name == expect:
            self.emit_event(emit)

    return on_event
