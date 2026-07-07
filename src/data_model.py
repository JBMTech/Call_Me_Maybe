from pydantic import BaseModel, Field, ValidationError


class DataObjectJSON(BaseModel):
    name: str
    description: str
    parameters: dict[str, dict[str, str]]
    returns: dict[str, str]
