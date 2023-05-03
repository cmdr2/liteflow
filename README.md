# liteflow

A lightweight library for event and workflow-based programming in Python. Inspired by DOM events, and uses native python datatypes for expressing the workflow concisely. Yet another workflow library.

## Installation
`pip install liteflow` (TBD)

## Example
```py
from liteflow import compile_workflow

example_workflow = [
    MyTask1(), { # run MyTask1, then conditionally branch based on "event_x" or "event_y"
       "event_x": [MyTaskX1(), MyTaskX2()], # run MyTaskX1, MyTaskX2 sequentially
       "event_y": [MyTaskY1(), { # run MyTaskY1, then run MyTaskY2a and MyTaskY2b in parallel
            MyTaskY2a(),
            MyTaskY2b()
        }],
    },
]
example_workflow = compile_workflow(example_workflow)

# run the workflow
example_workflow.dispatch_event("event_foo", "hello")
```

Please see the [example below](#example-implement-the-workflow-modules) for a sample implementation of the modules in this example.

## Why another workflow library?
The library focuses on concise expression of workflows, using native Python datatypes. The API is designed to be lightweight and familiar, so that it's easy to remember and be productive.

The workflow logic is represented by combining just three native datatypes:
* **list** - `[a, b, c]` - Modules `a`, `b`, `c` are run sequentially i.e. one-after-another. The output of `a` is fed into `b`, the output of `b` is fed into `c`
* **set** - `{a, b, c}` - Modules `a`, `b`, `c` are run in parallel. All three receive the same event from their parent module. The set outputs are currently unused.
* **dict** - `{"x": a, "y": b}` - Module `a` is run if the parent emits event `"x"`, module `b` is run if the parent emits event `"y"`. The key can also be a function (which takes the event as input, and returns `True` or `False`).

Workflow modules can be implemented by extending the `liteflow.Module` class.

Please see the [example](#example) and [API reference](#api-reference) below.

## Why write code as a workflow?
1. It's easy to visualize the logic of a complex system, at a single glance.
2. Each module can be unit-tested, and can focus on doing just one thing.
3. Non-technical users can write/modify the workflow logic, using visual programming. Maybe someone will write a visual programming plugin for liteflow, that produces liteflow-compatible workflow code?

## Example: Implement the workflow modules
The workflow has been defined in the [example](#example) above.

Now, let's write an example implementation for each of the workflow modules. In this example, `MyTask1` emits `"event_x"` or `"event_y"` at random. This will result in one of the two branches getting executed each time the workflow is run.

#### **A short note about event handlers:**

> The first argument sent to all the event handlers is `event_name` (string). This is mandatory.
>
> After that, there is no limitation on the number of arguments that can be sent to an event handler. Please ensure that the signature of the event handler functions matches the arguments being sent via `dispatch_event()` or `emit_event()`.
>
> In the example below, `MyTask1` accepts only one argument in the event handler for `"event_foo"` (other than `event_name`), while `MyTaskX1` does not accept any arguments in the event handler for `"event_x"`. So if the `"event_foo"` event is being sent to `MyTask1`, exactly one argument needs to be sent (other than `event_name`), and if `"event_x"` is being sent to `MyTaskX1`, no arguments should be sent (other than `event_name`).

#### Example implementation
```py
from liteflow import Module
import random

class MyTask1(Module):
    def __init__(self):
        self.add_event_listener("event_foo", self.on_foo)

    def on_foo(self, event_name: str, data):
        print("MyTask1. Got:", event_name, "data:", data)
        new_event_name = random.choice(("event_x", "event_y"))
        self.emit_event(new_event_name)

class MyTaskX1(Module):
    def __init__(self):
        self.add_event_listener("event_x", self.on_event)

    def on_event(self, event_name: str):
        print("MyTaskX1. Got:", event_name)
        self.emit_event("event_x1", 42, "question")

class MyTaskX2(Module):
    def __init__(self):
        self.add_event_listener("event_x1", self.on_event)

    def on_event(self, event_name: str, data, query):
        print("MyTaskX2. Got:", event_name, "data:", data, query)

class MyTaskY1(Module):
    def __init__(self):
        self.add_event_listener("event_y", self.on_event)

    def on_event(self, event_name: str):
        print("MyTaskY1. Got:", event_name)
        self.emit_event("event_y1")

class MyTaskY2a(Module):
    def __init__(self):
        self.add_event_listener("event_y1", self.on_event)

    def on_event(self, event_name: str):
        print("MyTaskY2a. Got:", event_name)


class MyTaskY2b(Module):
    def __init__(self):
        self.add_event_listener("*", self.on_event)

    def on_event(self, event_name: str, *args):
        print("MyTaskY2b. Got:", event_name, "data:", *args)
```

## API Reference
### compile_workflow
`compile_workflow(workflow)` returns a `liteflow.Module` instance, to which events can be sent.

This module serves as the starting point of the workflow.

### liteflow.Module
Extending from `liteflow.Module` adds three DOM-like event-handling methods:
* `add_event_listener(event_name: str, listener: function)`
* `dispatch_event(event_name: str, *args)`
* `remove_event_listener(event_name: str, listener: function)`.

`liteflow.Module` also adds three workflow-related methods, to send/receive data between modules in the workflow:
* `attach_output_listener(other_module: Module)`
* `emit_event(event_name: str, *args)`
* `detach_output_listener(other_module: Module)`
