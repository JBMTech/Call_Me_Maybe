import json
from pathlib import Path
from llm_sdk import Small_LLM_Model
from .data_model import FunctionDefinition, StructureContext
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
                tuple(self.get_tokens(x.name) + self.get_tokens('","')): [
                    tuple(self.get_tokens(y))
                    for y in x.parameters.keys()]
                for x in funct_def},
            param_start=tuple(self.get_tokens('parameters":{"')),
            param_names=[[self.get_tokens(y) for y in x.parameters.keys()]
                         for x in funct_def],
            param_types={[self.get_tokens(y) for y in x.parameters.values()]
                         for x in funct_def},
            kvsep=(tuple(self.get_tokens('":"'))),
            sep=tuple(self.get_tokens('","')),
            end=tuple(self.get_tokens('"}}\n')),
        )

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
        """
        Genera un JSON mediante constrained decoding.
        """
        # 1. Crear una copia del contexto
        context = self.structure_context.model_copy(deep=True)

        # 2. Crear el Builder inicial
        builder = BuilderFunction(context)

        # 3. Crear la salida
        output = []

        # 4. Construir el contexto del modelo
        output.extend(self.get_tokens(prompt))
        model_context = output

        # 5. Mientras exista un Builder
        while builder is not None:

            # Obtener los tokens permitidos (lista de las funciones permitidas)
            allowed = builder.get_allowed()

            # Si el Builder terminó automáticamente,
            # pasar al siguiente
            if not allowed:
                builder = builder.next_builder()
                continue

            # Obtener los logits del modelo
            logits = self.get_logits(model_context + output)

            # Elegir el mejor token permitido
            token = self.choose_best_token(logits, allowed)

            # Añadir el token
            builder = self.append_token(
                output,
                builder,
                token
            )

        # 6. Devolver el JSON generado
        return self.decode_token(output)
