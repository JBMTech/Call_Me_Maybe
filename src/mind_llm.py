from llm_sdk.llm_sdk import Small_LLM_Model


class LLMInterface:

    def __init__(self, model_name: str):
        self.model_name = Small_LLM_Model(model_name)
