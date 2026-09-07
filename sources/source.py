from abc import ABC, abstractmethod

from job import Job


class Source(ABC):
    @abstractmethod
    def fetch(self) -> list[Job]:
        pass

    