from pydantic import BaseModel, Field


class FunctionDefinition(BaseModel):
    """
    Represents a function definition loaded from
    ``functions_definition.json``.

    Attributes:
        name:
            Name of the function.
        description:
            Natural language description of the function.
        parameters:
            Dictionary describing the function parameters and their
            associated JSON types.
        returns:
            Dictionary describing the function return type.
    """
    name: str
    description: str
    parameters: dict[str, dict[str, str]]
    returns: dict[str, str]


class TestPrompt(BaseModel):
    """
    Represents a prompt loaded from
    ``function_calling_tests.json``.

    Attributes:
        prompt:
            Natural language prompt used as input for the language
            model.
    """
    prompt: str


class BuildJSON(BaseModel):
    """
    Represents a generated function call.

    This model validates the structure of the JSON objects written to
    ``function_calling_result.json``.

    Attributes:
        prompt:
            Original user prompt.
        name:
            Name of the selected function.
        parameters:
            Dictionary containing the generated parameter values.
    """
    prompt: str
    name: str
    parameters: dict[str, str | int | float | bool]


class FunctionContext(BaseModel):
    """
    Stores the decoding information associated with a single function.

    During constrained decoding, parameter names and parameter types
    are copied from this model into the active decoding context.

    Attributes:
        param_names:
            Tokenized parameter names.
        param_types:
            JSON type associated with each parameter.
    """
    param_names: list[tuple[int, ...]]
    param_types: list[str]


class StructureContext(BaseModel):
    """
    Shared context used during constrained decoding.

    This model stores the tokenized JSON grammar, the available
    functions, their parameters and the model vocabulary required by
    the different Builder states.

    Attributes:
        functions:
            Mapping between tokenized function names and their decoding
            context.

        param_start:
            Token sequence representing the beginning of the
            ``parameters`` object.

        param_names:
            Remaining parameter names to generate.

        param_types:
            JSON type associated with each remaining parameter.

        vocab:
            Vocabulary of the language model.

        kvsep:
            Token sequence representing the JSON key-value separator.

        sep:
            Token sequence separating two JSON parameters.

        end:
            Token sequence closing the generated JSON object.
    """
    functions: dict[
        tuple[int, ...],
        FunctionContext
    ]
    param_start: tuple[int, ...]
    param_names: list[tuple[int, ...]] = Field(default_factory=list)
    param_types: list[str] = Field(default_factory=list)
    vocab: list[str]
    kvsep: tuple[int, ...]
    sep: tuple[int, ...]
    end: tuple[int, ...]
