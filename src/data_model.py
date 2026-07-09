from pydantic import BaseModel


class FunctionDefinition(BaseModel):
    """Representa una función del archivo functions_definition.json."""

    name: str
    description: str
    parameters: dict[str, dict[str, str]]
    returns: dict[str, str]


class TestPrompt(BaseModel):
    prompt: str
