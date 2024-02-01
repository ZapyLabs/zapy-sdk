from typing import Any

from pydantic import BaseModel


class Attr(BaseModel):

    @staticmethod
    def create(path: str, field_name: str, attribute: Any) -> "Attr":
        return Attr(path=path, field_name=field_name, type_str=type(attribute).__name__, value_repr=repr(attribute))

    path: str
    field_name: str
    value_repr: str
    type_str: str
    attributes: list["Attr"] = []


def build_attr_info(attr: Any, path: str) -> Attr:
    attr_info = Attr.create(path, path, attribute=attr)
    for child_attr_name in dir(attr):
        if child_attr_name.startswith("__"):
            continue
        child_attr = getattr(attr, child_attr_name)
        if callable(child_attr):
            continue
        child_attr = Attr.create(f"{path}.{child_attr_name}", child_attr_name, attribute=child_attr)
        attr_info.attributes.append(child_attr)
    if isinstance(attr, dict):
        for k, v in attr.items():
            child_attr = Attr.create(f"{path}['{k}']", f"'{k}'", attribute=v)
            attr_info.attributes.append(child_attr)
    if isinstance(attr, (list, tuple)):
        for k, v in enumerate(attr):
            child_attr = Attr.create(f"{path}[{k}]", str(k), attribute=v)
            attr_info.attributes.append(child_attr)
    return attr_info
