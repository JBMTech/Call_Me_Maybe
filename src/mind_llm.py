import json
from pathlib import Path
from llm_sdk import Small_LLM_Model
from .data_model import FunctionDefinition, StateContext, BuildJSON
from .build_json import BuilderFunction, BuilderValue


class LLMInterface:

    def __init__(self,
                 model_name: str,
                 defs: list[FunctionDefinition]):
        self.model_name = Small_LLM_Model(model_name)
        self.vocal: list[str] = list()
