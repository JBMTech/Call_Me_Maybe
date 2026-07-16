import json
from pathlib import Path
from llm_sdk import Small_LLM_Model
from .data_model import FunctionDefinition, StructureContext, BuildJSON
from .build_json import BuilderFunction, BuilderValue


class LLMInterface:

    def __init__(self,
                 model_name: str,
                 funct_def: list[FunctionDefinition]):
        self.model = Small_LLM_Model(model_name)
        self.vocal: list[str] = list(json.loads(Path(self.model.get_path_to_vocab_file()).read_text()).keys())
        self.structure_contex = StructureContext(
            functions={
                tuple(self.get_tokens(x.name) + self.get_tokens('","')): [
                    tuple(self.get_tokens(y))
                    for y in x.parameters.keys()]
                for x in funct_def},
            parameters=tuple(self.get_tokens('parameters":{"')),
            kvsep=(tuple(self.get_tokens('":"'))),
            sep=tuple(self.get_tokens('","')),
            end=tuple(self.get_tokens('"}}\n')),
        )

    def get_tokens(self, string: str) -> list[int]:
        return self.model.encode(string)[0].tolist()
