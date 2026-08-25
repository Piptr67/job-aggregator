from dataclasses import dataclass

@dataclass
class Job:
    title: str
    description: str
    link: str
    pub_date: str
    company: str

    