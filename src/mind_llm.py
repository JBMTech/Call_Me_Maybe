import json
from pathlib import Path
from llm_sdk.llm_sdk import Small_LLM_Model
from .data_model import (
    FunctionDefinition,
    StructureContext,
    FunctionContext,
)
from .build_json import (
    Builder,
    BuilderFunction,
    BuilderValue
)
from typing import Any


class LLMInterface:
    """
    Interface responsible for interacting with the language model.

    This class initializes the LLM, prepares the constrained decoding
    context, and generates structured JSON function calls from natural
    language prompts.

    The decoding process combines unrestricted language model generation
    with Builder objects that constrain the JSON syntax.
    """
    def __init__(self,
                 model_name: str,
                 funct_def: list[FunctionDefinition]) -> None:
        self.model = Small_LLM_Model(model_name)
        self.vocab: list[str] = list(
            json.loads(Path(self.model.get_path_to_vocab_file()).read_text())
            .keys())
        self.structure_context = StructureContext(
            functions={
                tuple(self.get_tokens(func.name) + self.get_tokens('","')):
                FunctionContext(
                    param_names=[
                        tuple(self.get_tokens(param))
                        for param in func.parameters.keys()
                    ],
                    param_types=[
                        info["type"]
                        for info in func.parameters.values()
                    ]
                )
                for func in funct_def
            },
            param_start=tuple(self.get_tokens('parameters":{"')),
            vocab=self.vocab,
            kvsep=tuple(self.get_tokens('":"')),
            sep=tuple(self.get_tokens('","')),
            end=tuple(self.get_tokens('"}}\n')),
        )
        self.function_defs = funct_def

    def get_tokens(self, string: str) -> Any:
        return self.model.encode(string)[0].tolist()

    def get_logits(self, input_ids: list[int]) -> Any:
        return self.model.get_logits_from_input_ids(input_ids)

    def decode_token(self, tokens: list[int]) -> Any:
        return self.model.decode(tokens)

    def valid_len(self, text: str) -> int:
        """
        Determine the longest valid JSON string prefix.

        This method is used while generating parameter values. It detects
        where the language model starts generating JSON syntax belonging
        to the next field instead of the current value.

        Args:
            text:
                Decoded parameter value.

        Returns:
            int:
                Length of the longest prefix that is still a valid JSON
                string.
        """
        for i in range(1, len(text) + 1):
            try:
                json.loads(f'["{text[:i]}"]')
            except json.JSONDecodeError:
                return i - 1
        return len(text)

    def append_token(
            self, output: list[int],
            builder: Builder,
            token: int) -> Any:
        """
        Append a generated token to the current Builder.

        For regular Builders, the token is simply appended and the Builder
        advances once its expected sequence is complete.

        For BuilderValue, the generated value is continuously validated to
        ensure that only the valid JSON value is kept. Any extra characters
        produced by the language model are discarded before moving to the
        next Builder.

        Args:
            output:
                Tokens composing the generated JSON.
            builder:
                Active Builder controlling the decoding state.
            token:
                Token selected by the language model.

        Returns:
            Builder | None:
                Current Builder if generation should continue in the same
                state, the next Builder otherwise.
        """
        allowed = builder.get_allowed()

        if not builder.unconditional() and token not in allowed:
            return builder

        # -----------------------------
        # CASO NORMAL
        # -----------------------------
        if not isinstance(builder, BuilderValue):
            builder.tokens.append(token)
            output.append(token)

            if builder.is_complete():
                return builder.next_builder()

            return builder

        # -----------------------------
        # CASO BuilderValue
        # -----------------------------

        # Primera vez que entramos en este Builder
        if not builder.tokens:
            builder.output_start = len(output)

        builder.tokens.append(token)

        texto = self.decode_token(builder.tokens)

        longitud = self.valid_len(texto)

        # Sigue siendo un valor válido
        if longitud == len(texto):
            output.append(token)
            return builder

        # Hay basura después del valor

        texto_valido = texto[:longitud]

        tokens_validos = self.get_tokens(texto_valido)

        builder.tokens = tokens_validos

        # Sustituimos TODO el valor anterior
        output[:] = output[:builder.output_start]

        output.extend(tokens_validos)

        return builder.next_builder()

    def choose_best_token(
            self,
            logits: list[float],
            allowed: set[int]) -> int | None:
        """
        Select the highest-scoring valid token.

        Args:
            logits:
                Scores produced by the language model.
            allowed:
                Set of token IDs allowed by the current Builder.

        Returns:
            int:
                Token ID with the highest score among the allowed tokens.
        """
        best_token = None
        best_logit = float("-inf")

        for token in allowed:
            current_logit = logits[token]

            if current_logit > best_logit:

                best_logit = current_logit
                best_token = token

        return best_token

    def generate_json(self, prompt: str) -> Any:
        """
        Generate a JSON function call from a natural language prompt.

        The method performs constrained decoding by combining language
        model predictions with a sequence of Builder objects that enforce
        the JSON grammar.

        The generation process consists of:
            1. Copying the decoding context.
            2. Creating the initial Builder.
            3. Building the model prompt.
            4. Iteratively generating tokens.
            5. Validating each generated token.
            6. Decoding the final token sequence.

        Args:
            prompt:
                Natural language prompt.

        Returns:
            str:
                Generated JSON fragment containing the function name and
                parameters.
        """
        context = self.structure_context.model_copy(deep=True)

        builder: Builder | None = BuilderFunction(context)

        text = "You are an assistant that only outputs JSON.\n"
        text += "Available functions\n"

        for func in self.function_defs:
            text += f"Function: {func.name}\n"
            text += f"Description: {func.description}\n"
            text += f"Parameters: {func.parameters}\n\n"

        func_descript = self.get_tokens(text)

        model_context = (func_descript + self.get_tokens(prompt))

        output: list[int] = []

        while builder is not None:

            allowed: Any = builder.get_allowed()

            if not builder.unconditional() and not allowed:
                builder = builder.next_builder()
                continue

            logits = self.get_logits(model_context + output)

            if builder.unconditional():
                token = logits.index(max(logits))
            else:
                token = self.choose_best_token(logits, allowed)

            if token is None:
                break
            builder = self.append_token(output, builder, token)

        return self.decode_token(output)
