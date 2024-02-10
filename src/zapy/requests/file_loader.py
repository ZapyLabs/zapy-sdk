from dataclasses import dataclass
from pathlib import Path

from zapy.base import ZapyAuto


@dataclass
class ZapyFileInfo:
    file_location: Path
    mime_type: str | type[ZapyAuto]
    file_name: str


def load_file(
    relative_path: str | Path, mime_type: str | type[ZapyAuto], context_path: Path | str | None = None
) -> ZapyFileInfo:
    base_path_str = context_path or "."
    file_location = Path(base_path_str) / relative_path
    name = file_location.name

    return ZapyFileInfo(file_location, mime_type, name)
