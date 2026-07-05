from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class JobListing:
    title: str
    company: str
    url: str
    source: str
    description: str = ""
    location: str = ""
    posted_date: str = ""


class BaseSearcher(ABC):
    @abstractmethod
    def login(self) -> None:
        ...

    @abstractmethod
    def search(self, keywords: str, location: str = "remote", max_results: int = 10) -> list[JobListing]:
        ...

    @abstractmethod
    def scrape_description(self, job: JobListing) -> str:
        ...

    @abstractmethod
    def close(self) -> None:
        ...
