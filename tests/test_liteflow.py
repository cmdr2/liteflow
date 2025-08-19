import pytest
from liteflow import run


def test_1_0_run_sequential_tasks():
    def add_one(x):
        return x + 1

    def times_two(x):
        return x * 2

    workflow = [add_one, times_two]
    result = run(workflow, 3)
    assert result == 8  # (3 + 1) * 2


def test_2_0_run_branching_tasks_key_match():
    workflow = {"a": lambda x: x + "1", "b": lambda x: x + "2"}
    result = run(workflow, "a")
    assert result == ["a1"]


def test_2_1_run_branching_tasks_callable_key():
    def is_even(x):
        return x % 2 == 0

    workflow = {is_even: lambda x: x * 10, 3: lambda x: x + 5}
    result = run(workflow, 4)
    assert result == [40]


def test_2_2_run_branching_tasks_multiple_matches():
    def always_true(x):
        return True

    workflow = {always_true: lambda x: x + 1, 5: lambda x: x * 2}
    result = run(workflow, 5)
    assert result == [6, 10]


def test_2_3_run_with_dict_key_callable_true():
    def cond(x):
        return x > 0

    def action(x):
        return x + 10

    workflow = {cond: action}
    result = run(workflow, 1)
    assert result == [11]


def test_2_4_run_with_dict_key_equals_data():
    workflow = {5: lambda x: x * 2}
    result = run(workflow, 5)
    assert result == [10]


def test_2_5_run_with_dict_key_callable_false():
    def cond(x):
        return x < 0

    workflow = {cond: lambda x: x + 10}
    result = run(workflow, 1)
    assert result == []


def test_3_0_run_parallel_tasks():
    def add_one(x):
        return x + 1

    def times_two(x):
        return x * 2

    workflow = {add_one, times_two}
    result = run(workflow, 3)
    assert sorted(result) == [4, 6]


def test_4_0_run_callable_workflow():
    def square(x):
        return x * x

    result = run(square, 5)
    assert result == 25


def test_5_0_run_object_with_run_method():
    class Dummy:
        def run(self, x):
            return x + 10

    dummy = Dummy()
    result = run(dummy, 5)
    assert result == 15


def test_6_0_run_none_data():
    def return_hello(x):
        return "hello"

    result = run(return_hello)
    assert result == "hello"


def test_7_0_run_nested_structures():
    def f1(x):
        return x + [1]

    def f2(x):
        return x * 2

    workflow = [{lambda x: x % 2 == 0: f2}, f1]
    assert run(workflow, 2) == [4, 1]


def test_8_0_run_with_empty_list():
    assert run([], 10) == 10


def test_8_1_run_with_empty_dict():
    assert run({}, 10) == []


def test_8_2_run_with_empty_set():
    assert run(set(), 10) == []
