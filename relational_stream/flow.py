from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Flow(Generic[T]):
    events: list[T]

    def __init__(self, events: list[T]):
        self.events = events


class FlowDefinition(ABC, Generic[T]):
    @abstractmethod
    def is_first_event(self, event: T) -> bool:
        pass

    @abstractmethod
    def is_next_event(self, events: Flow[T], event: T) -> bool:
        pass

    @abstractmethod
    def is_complete(self, events: Flow[T]) -> bool:
        pass
