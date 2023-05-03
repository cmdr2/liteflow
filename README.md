# liteflow

A lightweight library for event and workflow-based programming in Python. Inspired by DOM events, and uses native python datatypes for expressing the workflow concisely. Yet another workflow library.

## Installation
`pip install liteflow` (TBD)

## Example
```py
from liteflow import compile_workflow, Event

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
e = Event("event_foo")
example_workflow.dispatch_event(e.type, e)
```

Please see the [example below](#example-implement-the-workflow-modules) for an example implementation of the modules in this example.

## Why another workflow library?
The library focuses on concise expression of workflows, using native Python datatypes. The API is designed to be lightweight and familiar, so that it's easy to remember and productive.

The workflow logic is represented by combining just three native datatypes:
* **list** - `[a, b, c]` - Modules `a`, `b`, `c` are run sequentially i.e. one-after-another. The output of `a` is fed into `b`, the output of `b` is fed into `c`
* **set** - `{a, b, c}` - Modules `a`, `b`, `c` are run in parallel. All three receive the same event from their parent module. The set outputs are currently unused.
* **dict** - `{"x": a, "y": b}` - Module `a` is run if the parent emit's event `"x"`, module `b` is run if the parent emit's event `"y"`. The key can also be a function (which takes the event as input, and returns `True` or `False`).

Workflow modules can be implemented by extending the `liteflow.Module` class.

Please see the [example](#example) and [API reference](#api-reference) below.

## Why write code as a workflow?
1. It's easy to visualize the logic of a complex system, at a single glance.
2. Each module can be unit-tested, and can focus on doing just one thing.
3. Non-technical users can write/modify the workflow logic, using visual programming. Maybe someone will write a visual programming plugin for liteflow, that produces liteflow-compatible workflow code?

## Example: Implement the workflow modules
The workflow has been defined in the [example](#example) above.

Now, let's write an example implementation for each of the workflow modules. In this example, `MyTask1` emits `"event_x"` or `"event_y"` at random. This will result in one of the two branches getting executed each time the workflow is run.

```py
from liteflow import Module, Event

class MyTask1(Module):
    def __init__(self):
        self.add_event_listener("event_foo", self.on_foo)

    def on_foo(self, event: Event):
        print("MyTask1. Got", event.type)
        import random
        new_event_type = random.choice(("event_x", "event_y"))
        e = Event(new_event_type)
        self.emit_event(e.type, e)

class MyTaskX1(Module):
    def __init__(self):
        self.add_event_listener("event_x", self.on_event)

    def on_event(self, event: Event):
        print("MyTaskX1. Got", event.type)
        e = Event("event_x1")
        self.emit_event(e.type, e)

class MyTaskX2(Module):
    def __init__(self):
        self.add_event_listener("*", self.on_event)

    def on_event(self, event: Event):
        print("MyTaskX2. Got", event.type)

class MyTaskY1(Module):
    def __init__(self):
        self.add_event_listener("event_y", self.on_event)

    def on_event(self, event: Event):
        print("MyTaskY1. Got", event.type)
        e = Event("event_y1")
        self.emit_event(e.type, e)

class MyTaskY2a(Module):
    def __init__(self):
        self.add_event_listener("*", self.on_event)

    def on_event(self, event: Event):
        print("MyTaskY2a. Got", event.type)


class MyTaskY2b(Module):
    def __init__(self):
        self.add_event_listener("*", self.on_event)

    def on_event(self, event: Event):
        print("MyTaskY2b. Got", event.type)
```

## API Reference
### compile_workflow
`compile_workflow(workflow)`

### liteflow.Module
Extending from `liteflow.Module` adds three DOM-like event-handling methods:
* `add_event_listener(event_type: str, listener: function)`
* `dispatch_event(event_type: str, event: Event)`
* `remove_event_listener(event_type: str, listener: function)`.

`liteflow.Module` also adds three workflow-related methods, to send/receive data between modules in the workflow:
* `attach_output_listener(other_module: Module)`
* `emit_event(event_type: str, event: Event)`
* `detach_output_listener(other_module: Module)`

### liteflow.Event
```py
class Event:
    type: str
    stop_propagation: bool = False
```
