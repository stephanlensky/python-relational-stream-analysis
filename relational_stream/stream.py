from typing import Generic, Type, TypeVar

from relational_stream.flow import Flow

T = TypeVar("T")
F = TypeVar("F", bound=Type[Flow])


class RelationalStream(Generic[T]):

    flow_types: list[Type[Flow[T]]]
    __incomplete_flows: dict[Type[Flow[T]], list[Flow[T]]]
    __complete_flows: dict[Type[Flow[T]], list[Flow[T]]]

    def __init__(self, flow_types: list[Type[Flow[T]]]) -> None:
        self.flow_types = flow_types
        self.__incomplete_flows = {flow_cls: [] for flow_cls in flow_types}
        self.__complete_flows = {flow_cls: [] for flow_cls in flow_types}

    def ingest(self, event: T):
        modified_flows: dict[Type[Flow[T]], set[Flow[T]]] = {
            flow_cls: set() for flow_cls in self.flow_types
        }

        for flow_cls in self.flow_types:

            # see if any new flows can be started from this event
            maybe_flow = flow_cls([])
            if maybe_flow.is_next_event(event):
                maybe_flow.add_event(event)
                self.__incomplete_flows[flow_cls].append(maybe_flow)
                modified_flows[flow_cls].add(maybe_flow)

            # see if any flows can use this event as their next element
            for flow in self.__incomplete_flows[flow_cls]:
                if flow.is_next_event(event) and flow not in modified_flows:
                    flow.add_event(event)
                    modified_flows[flow_cls].add(flow)

        # finally check if the addition of this event has completed any flows
        for flow_cls in self.flow_types:
            for flow in modified_flows[flow_cls]:
                if flow.is_complete():
                    self.__incomplete_flows[flow_cls].remove(flow)
                    self.__complete_flows[flow_cls].append(flow)

    def incomplete_flows(self, flow_type: Type[F]) -> list[F]:
        return self.__incomplete_flows[flow_type]  # type: ignore

    def completed_flows(self, flow_type: Type[F]) -> list[F]:
        return self.__complete_flows[flow_type]  # type: ignore
