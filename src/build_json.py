from abc import ABC, abstractmethod
from .data_model import StructureContext


class Builder(ABC):
    def __init__(self, context: StructureContext):
        super().__init__()
        self.context = context
        self.tokens: list[int] = []

    def _valid_tokens(self, options: tuple[tuple[int, ...], ...]) -> set[int]:
        result: set[int] = set()

        if not self.tokens:
            return {x[0] for x in options}
        for option in options:
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
    def next_builder(self) -> "Builder | None":
        raise NotImplementedError()


class BuilderEnd(Builder):
    def get_allowed(self) -> set[int]:
        return self._valid_tokens((self.context.end,))

    def next_builder(self) -> None:
        return None


class BuilderSep(Builder):
    def get_allowed(self) -> set[int]:
        return self._valid_tokens((self.context.sep,))

    def next_builder(self) -> Builder:
        return BuilderKey(self.context)


class BuilderValue(Builder):
    ...


class BuilderKVSep(Builder):
    def get_allowed(self) -> set[int]:
        return self._valid_tokens((self.context.kvsep,))

    def next_builder(self) -> Builder:
        return BuilderValue(self.context)


class BuilderKey(Builder):
    def get_allowed(self) -> set[int]:
        return self._valid_tokens((self.context.parameters[0],))

    def next_builder(self) -> Builder:
        self.context.parameters.pop(0)
        return BuilderKVSep(self.context)


class BuilderParameters(Builder):
    def get_allowed(self) -> set[int]:
        return self._valid_tokens((self.context.parameters,))

    def next_builder(self) -> Builder:
        return BuilderKey(self.context)


class BuilderFunction(Builder):
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(tuple(self.context.functions.keys()))

    def next_builder(self) -> Builder:
        self.context.parameters = \
            self.context.functions[tuple(self.tokens)].copy()
        return BuilderParameters(self.context)
