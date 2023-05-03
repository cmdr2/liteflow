# liteflow

A lightweight library for event and workflow-based programming in Python. Inspired by DOM events, and uses basic python datatypes for expressing the workflow concisely. Yet another workflow library.

## Installation
`pip install liteflow` (TBD)

## Why another workflow library?
The library focuses on concise expression of workflows, using native Python datatypes. The entire API can be kept in the head, and is described below.

The workflow logic is represented by combining just three native datatypes:
* **list** - `[a, b, c]` - Modules `a`, `b`, `c` are run sequentially i.e. one-after-another. The output of `a` is fed into `b`, whose output is fed into `c`
* **set** - `{a, b, c}` - Modules `a`, `b`, `c` are run in parallel. All three receive the same event from their parent module. The set outputs are currently unused.
* **dict** - `{"x": a, "y": b}` - Module `a` is run if the parent emit's event `"x"`, `b` is run if the parent emit's event `"y"`. The key can also be a function (which takes the event as input, and returns `True` or `False`).

Workflow modules can be implemented by extending the `liteflow.Module` class. This adds three DOM-like event-handling methods:
* `add_event_listener(event_type: str, listener: function)`
* `dispatch_event(event_type: str, event: Event)`
* `remove_event_listener(event_type: str, listener: function)`.

`liteflow.Module` also adds three workflow-related methods, to send/receive data between modules in the workflow:
* `attach_output_listener(other_module: Module)`
* `emit_event(event_type: str, event: Event)`
* `detach_output_listener(other_module: Module)`

## Example
### Describe the workflow
```py
from liteflow import compile_workflow, Event

example_workflow = [
    MyTask1, {
       "event_x": [MyTaskX1, MyTaskX2],
       "event_y": [MyTaskY1, {MyTaskY2a, MyTaskY2b}],
    },
]
example_workflow = compile_workflow(example_workflow)

# run the workflow
e = Event("event_foo")
example_workflow.dispatch_event(e.type, e)
```

**Explanation of the workflow:**

This example runs `MyTask1` first. It then checks whether the emitted event is of type `"event_x"`, or `"event_y"`.

If `MyTask1` emits event.type `"event_x"`, it feeds that event to `MyTaskX1` and then runs `MyTaskX2` one-after-another (i.e. sequentially).
Otherwise if `MyTask1` emits event.type `"event_y"`, then it feeds that event to `MyTaskY1`. After that, it runs `MyTaskY2a` and `MyTaskY2b` in parallel. Both `MyTaskY2a` and `MyTaskY2b` receive the same input, i.e. the event emitted by `MyTaskY1`.

### Implement the workflow modules
Now, let's write an example implementation of the workflow modules. In this example, `MyTask1` emits `"event_x"` or `"event_y"` at random. This will result in one of the two branches getting executed each time the workflow is run.

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