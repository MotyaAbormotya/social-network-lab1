from pathlib import Path
from typing import Protocol

from domain.models import Data


class NetworkRepository(Protocol):
    def read(self, path: Path) -> dict[str, object]: ...
    def write(self, path: Path, data: Data): ...
