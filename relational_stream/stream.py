from typing import Generic, TypeVar

from relational_stream.flow import Flow, FlowDefinition

T = TypeVar("T")


class RelationalStream(Generic[T]):

    flow_definitions: list[FlowDefinition[T]]
    incomplete_flows: dict[FlowDefinition[T], set[Flow[T]]]
    complete_flows: dict[FlowDefinition[T], set[Flow[T]]]

    def __init__(self, flow_definitions: list[FlowDefinition[T]]) -> None:
        self.flow_definitions = flow_definitions
        self.incomplete_flows = {flow_def: set() for flow_def in flow_definitions}
        self.complete_flows = {flow_def: set() for flow_def in flow_definitions}

    def ingest(self, event: T):
        modified_flows: dict[FlowDefinition[T], set[Flow[T]]] = {
            flow_def: set() for flow_def in self.flow_definitions
        }

        # see if any new flows can be started from this event
        for flow_def in self.flow_definitions:
            if flow_def.is_first_event(event):
                flow = Flow([event])
                self.incomplete_flows[flow_def].add(flow)
                modified_flows[flow_def].add(flow)

        # otherwise see if any flows can use this event as their next element
        for flow_def in self.flow_definitions:
            for flow in self.incomplete_flows[flow_def]:
                if flow_def.is_next_event(flow, event) and flow not in modified_flows:
                    self.incomplete_flows[flow_def].add(flow)
                    modified_flows[flow_def].add(flow)

        # finally check if the addition of this event has completed any flows
        for flow_def in self.flow_definitions:
            for flow in modified_flows[flow_def]:
                if flow_def.is_complete(flow):
                    self.incomplete_flows[flow_def].remove(flow)
                    self.complete_flows[flow_def].add(flow)
