import json
from pathlib import Path
from llm_sdk import Small_LLM_Model
from .data_model import (
    FunctionDefinition,
    StructureContext,
    FunctionContext,
)
from .build_json import Builder, BuilderFunction


class LLMInterface:

    def __init__(self,
                 model_name: str,
                 funct_def: list[FunctionDefinition]):
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
            # param_names=[],
            # param_types=[],
            vocab=self.vocab,
            kvsep=tuple(self.get_tokens('":"')),
            sep=tuple(self.get_tokens('","')),
            end=tuple(self.get_tokens('"}}\n')),
        )
        self.function_defs = funct_def

    def get_tokens(self, string: str) -> list[int]:
        return self.model.encode(string)[0].tolist()

    def get_logits(self, input_ids: list[int]) -> list[float]:
        return self.model.get_logits_from_input_ids(input_ids)

    def decode_token(self, tokens: list[int]) -> str:
        return self.model.decode(tokens)

    def append_token(self, output: list[int], builder: Builder, token: int):
        """ 1. Obtener los tokens permitidos.
        2. Si el token no está permitido → salir.
        3. Añadir el token al Builder.
        4. Añadir el token a output.
        5. Si el Builder ha terminado: devolver builder.next_builder()
        6. Si no: seguir con el mismo Builder.
        """
        allowed = builder.get_allowed()
        if token not in allowed:
            return builder
        builder.tokens.append(token)
        output.append(token)
        if builder.is_complete():
            return builder.next_builder()
        return builder

    def choose_best_token(self, logits: list[float], allowed: set[int]) -> int:

        best_token = None
        best_logit = float("-inf")

        for token in allowed:
            current_logit = logits[token]

            if current_logit > best_logit:

                best_logit = current_logit
                best_token = token

        return best_token

    def generate_json(self, prompt: str) -> str:

        # 1. Copiar el contexto
        context = self.structure_context.model_copy(deep=True)

        # 2. Crear el primer Builder
        builder = BuilderFunction(context)

        # 3. Tokens del prompt (solo contexto del modelo)
        text = ""

        for func in self.function_defs:
            text += f"Function: {func.name}\n"
            text += f"Description: {func.description}\n\n"
            # text += f"Return: {func.returns}\n\n"

        func_descript = self.get_tokens(text)

        model_context = (func_descript + self.get_tokens(prompt))

        # 4. Salida del JSON
        output = []

        # 5. Generación restringida
        while builder is not None:

            allowed = builder.get_allowed()

            if not allowed:
                builder = builder.next_builder()
                continue

            logits = self.get_logits(model_context + output)

            token = self.choose_best_token(logits, allowed)

            builder = self.append_token(output, builder, token)

        # 6. Decodificar
        return self.decode_token(output)
