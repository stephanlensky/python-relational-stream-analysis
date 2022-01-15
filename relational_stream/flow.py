from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Flow(ABC, Generic[T]):
    events: list[T]

    def __init__(self, events: list[T]):
        self.events = events

    def add_event(self, event: T) -> None:
        self.events.append(event)

    @abstractmethod
    def is_next_event(self, event: T) -> bool:
        pass

    @abstractmethod
    def is_complete(self) -> bool:
        pass
