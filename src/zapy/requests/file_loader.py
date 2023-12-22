from pathlib import Path
from dataclasses import dataclass


@dataclass
class ZapyFileInfo:
    """Class for keeping track of an item in inventory."""
    file_location: Path
    mime_type: str
    file_name: str


def load_file(relative_path: str, mime_type, context_path=None):
    base_path_str = context_path or '.'
    file_location = Path(base_path_str) / relative_path
    name = file_location.name
    
    return ZapyFileInfo(file_location, mime_type, name)
