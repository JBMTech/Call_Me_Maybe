import json
from pathlib import Path
from llm_sdk import Small_LLM_Model
from .data_model import FunctionDefinition, StructureContext, BuildJSON
from .build_json import Builder


class LLMInterface:

    def __init__(self,
                 model_name: str,
                 funct_def: list[FunctionDefinition]):
        self.model = Small_LLM_Model(model_name)
        self.vocab: list[str] = list(
            json.loads(Path(self.model.get_path_to_vocab_file()).read_text())
            .keys())
        self.structure_contex = StructureContext(
            functions={
                tuple(self.get_tokens(x.name) + self.get_tokens('","')): [
                    tuple(self.get_tokens(y))
                    for y in x.parameters.keys()]
                for x in funct_def},
            parameters=[tuple(self.get_tokens('parameters":{"'))],
            kvsep=(tuple(self.get_tokens('":"'))),
            sep=tuple(self.get_tokens('","')),
            end=tuple(self.get_tokens('"}}\n')),
        )

    def get_tokens(self, string: str) -> list[int]:
        return self.model.encode(string)[0].tolist()

    def get_logits_ids(self, list: list[int]) -> list[float]:
        return self.model.get_logits_from_input_ids(list)

    def decode_token(self, tokens: int) -> str:
        return self.model.decode(tokens)

    def appened_token(self, output: list[int], builder: Builder, token: int):
        """
        1. Obtener los tokens permitidos.

        2. Si el token no está permitido → salir.

        3. Añadir el token al Builder.

        4. Añadir el token a output.

        5. Si el Builder ha terminado:
            devolver builder.next_builder()

        6. Si no:
            seguir con el mismo Builder.
        """
        ...

    def generate_json(prompt: str):
        ...
