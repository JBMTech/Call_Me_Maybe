from pydantic import BaseModel


class FunctionDefinition(BaseModel):
    """Representa una función del archivo functions_definition.json."""
    name: str
    description: str
    parameters: dict[str, dict[str, str]]
    returns: dict[str, str]


class TestPrompt(BaseModel):
    """Representa el prompt del archivo funtions_calling_tests.json"""
    prompt: str


class BuildJSON(BaseModel):
    """Representa la estructura de function_calling_results.json"""
    prompt: str
    name: str
    parameters: dict[str, str | int | float | bool]


class StructureContext(BaseModel):
    # Funciones disponibles y sus parámetros
    functions: dict[tuple[int, ...], list[tuple[int, ...]]]

    # Token fijo: parameters":{
    param_start: tuple[int, ...]

    # Parámetros que faltan por escribir
    param_names: list[tuple[int, ...]] = []

    # Tipo de cada parámetro
    param_types: dict[str, str] = {}

    # Separadores del JSON
    kvsep: tuple[int, ...]
    sep: tuple[int, ...]
    end: tuple[int, ...]
