from .types import Module

from typing import Union


class SequentialModule(Module):
    def __init__(self, modules):
        self.modules = modules

        for i in range(len(modules) - 1):
            modules[i].attach_output_listener(modules[i + 1])

    def dispatch_event(self, event_name, event):
        self.modules[0].dispatch_event(event_name, event)

    def attach_output_listener(self, module):
        self.modules[-1].attach_output_listener(module)


class ParallelModule(Module):
    pass


class ConditionalModule(Module):
    def __init__(self, map: dict[str, Module]):
        self.map = map
        self.add_event_listener("*", self.on_event)

    def on_event(self, event):
        for event_name, module in map.items():
            self.add_event_listener(event_name, lambda n, e: module.dispatch_event(n, e))


def compile_workflow(workflow: Union[list, set, dict, Module], parent: Module = None) -> Module:
    if workflow is None or (isinstance(workflow, (list, set, dict)) and len(workflow) == 0):
        return

    if isinstance(workflow, Module):
        return workflow

    if isinstance(workflow, list):
        for i in range(0, len(workflow) - 1):
            target = compile_workflow(workflow[i + 1], parent if i == 0 else workflow[i])
            workflow[i].attach_output_listener(target)

        return workflow[0]

    if isinstance(workflow, set):
        pass
