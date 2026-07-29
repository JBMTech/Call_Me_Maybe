from abc import ABC, abstractmethod
from .data_model import StructureContext


class Builder(ABC):
    def __init__(self, context: StructureContext):
        super().__init__()
        self.context = context
        self.tokens: list[int] = []

    def _valid_tokens(self, input_tokens:
                      tuple[tuple[int, ...], ...]) -> set[int]:
        result: set[int] = set()

        if not self.tokens:
            return {x[0] for x in input_tokens}
        for option in input_tokens:
            if len(option) <= len(self.tokens):
                continue
            for option_token, token in zip(option, self.tokens):
                if option_token != token:
                    break
            else:
                result.add(option[len(self.tokens)])
        return result

    @abstractmethod
    def get_allowed(self) -> set[int]:
        raise NotImplementedError()

    @abstractmethod
    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        ...

    @abstractmethod
    def next_builder(self) -> "Builder | None":
        raise NotImplementedError()

    def is_complete(self) -> bool:
        for sequence in self.expected_sequences():
            if tuple(self.tokens) == sequence:
                return True
        return False

    def unconditional(self) -> bool:
        return False


class BuilderEnd(Builder):
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(self.expected_sequences())

    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        return (self.context.end,)

    def next_builder(self) -> None:
        return None


class BuilderSep(Builder):
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(self.expected_sequences())

    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        return (self.context.sep,)

    def next_builder(self) -> Builder:
        if self.context.param_names:
            return BuilderKey(self.context)
        return BuilderEnd(self.context)


class BuilderValue(Builder):
    
    def __init__(self, context):
        super().__init__(context)

        # Posición donde empieza este valor dentro del output.
        self.output_start = 0

    def unconditional(self) -> bool:
        return True

    def get_allowed(self) -> set[int]:
        return set()

    def current_text(self) -> str:
        """
        Obtenemos el texto actual de tokens.
        """
        return "".join(self.context.vocab[token]
                       for token in self.tokens)

    def expected_sequences(self):
        return ()

    def is_complete(self):
        return len(self.tokens) > 0

    def next_builder(self) -> "Builder | None":
        self.context.param_names.pop(0)
        self.context.param_types.pop(0)

        if self.context.param_names:
            return BuilderSep(self.context)

        return BuilderEnd(self.context)


class BuilderKVSep(Builder):
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(self.expected_sequences())

    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        return (self.context.kvsep,)

    def next_builder(self) -> Builder:
        return BuilderValue(self.context)


class BuilderKey(Builder):
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(self.expected_sequences())

    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        return (self.context.param_names[0],)

    def next_builder(self) -> Builder:
        return BuilderKVSep(self.context)


class BuilderParameter_start(Builder):
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(self.expected_sequences())

    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        return (self.context.param_start, )

    def next_builder(self) -> Builder:
        return BuilderKey(self.context)


class BuilderFunction(Builder):
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(self.expected_sequences())

    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        return tuple(self.context.functions.keys())

    def next_builder(self) -> Builder:
        function = self.context.functions[tuple(self.tokens)]
        self.context.param_names = function.param_names.copy()
        self.context.param_types = function.param_types.copy()
        return BuilderParameter_start(self.context)
