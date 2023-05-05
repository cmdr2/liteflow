# liteflow (beta)

A lightweight library for event and workflow-based programming in Python. Uses native python datatypes for expressing the workflow concisely. Modules inspired by DOM Events. Yet another workflow library.

Workflow tasks can be implemented as regular python functions, or class objects that implement the `__call__()` method, or as sub-classes of the `liteflow.Module` class.

A task function will be sent the output of the previous task. A task function has to accept atleast one argument. This is the only requirement.

## Installation
`pip install liteflow` (TBD)

## Example
```py
from liteflow import compile_workflow

example_workflow = [
    task_1, { # run `task_1()`, then branch conditionally based on the return value of task_1
       "event_x": [task_x1, task_x2], # run `task_x1()` and `task_x2()` one-after-another (i.e sequentially)
       "event_y": [task_y1, { # or, run `task_y1()`, then run `task_y2a()` and `task_y2b()` in parallel
            task_y2a,
            task_y2b
        }],
    },
]
example_workflow = compile_workflow(example_workflow)

# run the workflow
example_workflow.dispatch_event("event_foo", "hello")
```

A visual representation of this workflow is:

![Untitled](https://user-images.githubusercontent.com/844287/235950815-4abb1556-1746-40d6-8cb5-69a8e81f95ed.jpg)

Please see the [example below](#example-implement-the-workflow-tasks) for a sample implementation of the tasks in this example.

## Why another workflow library?
The library focuses on concise expression of workflows, using native Python datatypes. The API is designed to be lightweight and familiar, so that it's easier to remember and be productive.

The workflow logic is represented by combining just three native datatypes:
* **list** - `[a, b, c]` - Tasks `a`, `b`, `c` are run sequentially i.e. one-after-another. The output of `a` is fed into `b`, and the output of `b` is fed into `c`.
* **set** - `{a, b, c}` - Tasks `a`, `b`, `c` are run in parallel. All three receive the same input (i.e. the data returned from the previous task).
* **dict** - `{"x": a, "y": b}` - Task `a` is run if the parent emits `"x"`, task `b` is run if the parent emits `"y"`. The dictionary key can also be a function (which receives the previous task's output, and needs to return `True` or `False`).

Workflows can be nested. The outputs from a `set` or `dict` workflow will be batched and emitted one by one to the attached task. The output from the last task in a `list` workflow will be emitted to the next task.

Workflow tasks can be implemented as regular python functions, or class objects that implement the `__call__()` method, or as sub-classes of the `liteflow.Module` class.

Please see the [example](#example) and [API reference](#api-reference) below.

## Why write code as a workflow?
1. It's easy to visualize the logic of a complex system, at a single glance.
2. Each task can be unit-tested, and can focus on doing just one thing.
3. Non-technical users can write/modify the workflow logic, using visual programming. Maybe someone will write a visual programming plugin for liteflow, that produces liteflow-compatible workflow code?

## Example: Implement the workflow tasks
The workflow has been defined in the [example](#example) above.

Now, let's write an example implementation for each of the workflow tasks. In this example, `task_1` emits `"event_x"` or `"event_y"` at random. This will result in one of the two branches getting executed each time the workflow is run.

#### **A short note about task functions:**

> A task function has to accept a minimum of one argument. This is mandatory.
>
> There is no upper limit on the number of arguments that can be sent to a task function. Please ensure that the number of arguments in a task function matches the number of values sent by the previous task.
>
> In the example below, `task_1` accepts only one extra argument (other than the mandatory first argument), while `task_x1` does not accept any extra arguments. So if the `"event_foo"` event is being sent to `task_1`, exactly one extra argument needs to be sent, and if `"event_x"` is being sent to `task_x1`, no extra arguments should be sent.
>
> If a task function does not return anything, the next function will receive `None` as the first argument.

#### Simple implementation (using python functions)
```py
import random

def task_1(a, b):
    print("task 1. Got:", a, b)
    return random.choice(("event_x", "event_y"))

def task_x1(a):
    print("task x1. Got:", a)
    return "event_x1", 42, "question"

def task_x2(a, b, c):
    print("task x2. Got:", a, b, c) # prints `task x2. Got: "event_x1" 42 "question"`

def task_y1(a):
    print("task y1. Got:", a)
    return "event_y1"

def task_y2a(a):
    print("task y2a. Got:", a)

def task_y2b(a, *args):
    print("task y2b. Got:", a, args)
```

## API Reference
### compile_workflow
`compile_workflow(workflow)` returns a `liteflow.Module` instance, to which events can be sent.

This module serves as the starting point of the workflow.

### liteflow.Module
Extending from `liteflow.Module` adds 6 methods. Three DOM-like event-handling methods, and three workflow-related methods (to send/receive data between modules in the workflow).

* `add_event_listener(event_name: str, listener: function)`
* `dispatch_event(event_name: str, *args)`
* `remove_event_listener(event_name: str, listener: function)`

* `attach_output_listener(other_module: Module)`
* `emit_event(event_name: str, *args)`
* `detach_output_listener(other_module: Module)`
