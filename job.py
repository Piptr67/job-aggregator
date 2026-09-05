from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    title: str
    description: str
    link: str
    pub_date: str
    company: str
