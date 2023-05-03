from liteflow import compile_workflow, Module
from liteflow.workflow import SequentialModule, ParallelModule, ConditionalModule


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
    m = compile_workflow(workflow)

    assert isinstance(m, SequentialModule)
    assert not hasattr(m, "output_listeners")
    assert not hasattr(workflow, "output_listeners")


def test_2_1_list__internal_modules_are_linked_sequentially():
    workflow = [Module(), Module(), Module()]
    m = compile_workflow(workflow)

    assert hasattr(workflow[0], "output_listeners")
    assert hasattr(workflow[1], "output_listeners")
    assert not hasattr(workflow[2], "output_listeners")

    assert workflow[1] in workflow[0].output_listeners
    assert workflow[2] in workflow[1].output_listeners
    assert len(workflow[0].output_listeners) == 1
    assert len(workflow[1].output_listeners) == 1


def test_2_2_list__call_to_sequential_invokes_first_module():
    workflow = [Module(), Module(), Module()]
    m = compile_workflow(workflow)


def test_2_3_list__nested_lists_are_linked_to_the_parent():
    workflow = [Module(), [Module(), Module()]]
    compile_workflow(workflow)

    assert workflow[1][0] in workflow[0].output_listeners
    assert len(workflow[0].output_listeners) == 1
    assert workflow[1][1] in workflow[1][0].output_listeners
    assert len(workflow[1][0].output_listeners) == 1


def test_2_4_list__nested_lists_join_after_finishing_nesting__NOT_IMPLEMENTED():
    # workflow = [Module(), [Module(), Module()], Module()]
    # compile_workflow(workflow)

    # assert workflow[1][0] in workflow[0].output_listeners
    # assert len(workflow[0].output_listeners) == 1
    # assert workflow[1][1] in workflow[1][0].output_listeners
    # assert len(workflow[1][0].output_listeners) == 1

    # assert workflow[2] in workflow[1][1].output_listeners
    # assert not hasattr(workflow[2], "output_listeners")
    pass


def test_3_1_set__first_module_is_returned():
    m1, m2 = Module(), Module()
    workflow = {m1, m2}
    assert compile_workflow(workflow) == m1


def test_3_2_set__modules_are_linked_in_parallel_to_the_set_parent():
    m1, m2 = Module(), Module()
    parent = Module()
    workflow = {m1, m2}
