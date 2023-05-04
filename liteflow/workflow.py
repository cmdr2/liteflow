from .types import Module

from typing import Union, Callable


class SequentialModule(Module):
    def __init__(self, modules: list[Module]):
        self.modules = [compile_workflow(m) for m in modules]

        for i in range(len(self.modules) - 1):
            self.modules[i].attach_output_listener(self.modules[i + 1])

    def dispatch_event(self, event_name, *args):
        self.modules[0].dispatch_event(event_name, *args)

    def attach_output_listener(self, module):
        self.modules[-1].attach_output_listener(module)


class BufferedOutputModule(Module):
    def __init__(self, modules: list[Module]) -> None:
        self.output_buffer = []

        output_buffer_module = Module()
        for m in modules:
            m.attach_output_listener(output_buffer_module)

        output_buffer_module.add_event_listener("*", self.buffer_event)

    def emit_buffered_events(self):
        for e, e_args in self.output_buffer:
            self.emit_event(e, *e_args)

        self.output_buffer.clear()

    def buffer_event(self, event_name, *args):
        self.output_buffer.append((event_name, args))


class ParallelModule(BufferedOutputModule):
    def __init__(self, modules: list[Module]):
        self.modules = [compile_workflow(m) for m in modules]

        super().__init__(self.modules)

    def dispatch_event(self, event_name, *args):
        for m in self.modules:
            m0 = compile_workflow(m)
            m0.dispatch_event(event_name, *args)

        self.emit_buffered_events()


class ConditionalModule(BufferedOutputModule):
    def __init__(self, modules_map: dict[str | Callable, Module]):
        self.modules_map = {k: compile_workflow(m) for k, m in modules_map.items()}

        super().__init__(self.modules_map.values())

    def dispatch_event(self, event_name: str, *args):
        for key, m in self.modules_map.items():
            if (isinstance(key, str) and key == event_name) or (callable(key) and key(event_name, *args)):
                m.dispatch_event(event_name, *args)

        self.emit_buffered_events()


def compile_workflow(workflow: Union[list, set, dict, Module]) -> Module:
    if isinstance(workflow, Module):
        return workflow

    if isinstance(workflow, list) and len(workflow) > 0:
        return SequentialModule(workflow)

    if isinstance(workflow, set) and len(workflow) > 0:
        return ParallelModule(workflow)

    if isinstance(workflow, dict) and len(workflow) > 0:
        return ConditionalModule(workflow)

    return None
