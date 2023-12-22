from pydantic import BaseModel, Field


class Metadata(BaseModel):
    v: str
    cell_type: str
    tags: list[str] = Field(default_factory=list)


class ZapyCell:
    metadata: Metadata
