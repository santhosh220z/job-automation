from dataclasses import dataclass
from abc import ABC, abstractmethod
from pathlib import Path


@dataclass
class ApplicationResult:
    success: bool
    company: str
    role: str
    url: str
    message: str = ""


class BaseApplicator(ABC):
    @abstractmethod
    def apply(self, url: str, resume_path: Path, cover_letter: str = "") -> ApplicationResult:
        ...
