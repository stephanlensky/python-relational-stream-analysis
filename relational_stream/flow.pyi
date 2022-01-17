import abc
from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar('T')

class Flow(ABC, metaclass=abc.ABCMeta):
    events: list[T]
    def __init__(self, events: list[T]) -> None: ...
    def add_event(self, event: T) -> None: ...
    @abstractmethod
    def is_next_event(self, event: T) -> bool: ...
    @abstractmethod
    def is_complete(self) -> bool: ...
