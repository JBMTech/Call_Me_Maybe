from abc import ABC, abstractmethod
from .data_model import StructureContext


class Builder(ABC):
    """
    Abstract base class representing a state in the constrained
    decoding process.

    Each Builder defines which tokens are valid at a given point of
    the JSON generation and determines the next state once its
    expected sequence has been completed.

    Attributes:
        context (StructureContext):
            Shared decoding context containing the JSON grammar.
        tokens (list[int]):
            Tokens generated while this state is active.
    """
    def __init__(self, context: StructureContext):
        super().__init__()
        self.context = context
        self.tokens: list[int] = []

    def _valid_tokens(self, input_tokens:
                      tuple[tuple[int, ...], ...]) -> set[int]:
        """
        Compute the set of valid next tokens.

        Given one or more valid token sequences, this method returns only
        the tokens that may legally follow the tokens already generated
        by the current Builder.

        Args:
            input_tokens:
                Tuple containing one or more valid token sequences.

        Returns:
            set[int]:
                Set of token IDs that are valid as the next generated token.
        """
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
        """
        Return the set of tokens that are valid in the current state.

        Returns:
            set[int]:
                Valid token IDs.
        """
        raise NotImplementedError()

    @abstractmethod
    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        """
        Return the token sequences accepted by this Builder.

        Returns:
            tuple[tuple[int, ...], ...]:
                Expected token sequences.
        """
        ...

    @abstractmethod
    def next_builder(self) -> "Builder | None":
        """
        Return the next Builder after completing the current state.

        Returns:
            Builder | None:
                The next Builder in the decoding process, or None if the
                JSON generation has finished.
        """
        raise NotImplementedError()

    def is_complete(self) -> bool:
        """
        Check whether the current Builder has completed its expected
        sequence.

        Returns:
            bool:
                True if the Builder has finished generating its sequence,
                False otherwise.
        """
        for sequence in self.expected_sequences():
            if tuple(self.tokens) == sequence:
                return True
        return False

    def unconditional(self) -> bool:
        return False


class BuilderEnd(Builder):
    """
    Final Builder responsible for closing the generated JSON object.
    """
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(self.expected_sequences())

    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        return (self.context.end,)

    def next_builder(self) -> None:
        return None


class BuilderSep(Builder):
    """
    Builder responsible for generating the separator between JSON
    parameters (",").
    """
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(self.expected_sequences())

    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        return (self.context.sep,)

    def next_builder(self) -> Builder:
        if self.context.param_names:
            return BuilderKey(self.context)
        return BuilderEnd(self.context)


class BuilderValue(Builder):
    """
    Builder responsible for generating parameter values.

    Unlike the other Builders, parameter values are generated freely
    by the language model instead of being restricted to predefined
    token sequences.

    The generated value is later validated and truncated to ensure
    that it forms a valid JSON value before the decoding process
    continues.
    """
    def __init__(self, context: StructureContext) -> None:
        super().__init__(context)
        self.output_start = 0

    def unconditional(self) -> bool:
        """
        Indicate that this Builder does not restrict token generation.

        Returns:
            bool:
                Always True for BuilderValue.
        """
        return True

    def get_allowed(self) -> set[int]:
        return set()

    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        return ()

    def is_complete(self) -> bool:
        return len(self.tokens) > 0

    def next_builder(self) -> "Builder | None":
        """
        Advance to the next parameter or finish the JSON object.

        Removes the processed parameter from the context and returns
        the appropriate Builder.

        Returns:
            Builder | None:
                BuilderSep if more parameters remain, otherwise BuilderEnd.
        """
        self.context.param_names.pop(0)
        self.context.param_types.pop(0)

        if self.context.param_names:
            return BuilderSep(self.context)

        return BuilderEnd(self.context)


class BuilderKVSep(Builder):
    """
    Builder responsible for generating the key-value separator (":").
    """
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(self.expected_sequences())

    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        return (self.context.kvsep,)

    def next_builder(self) -> Builder:
        return BuilderValue(self.context)


class BuilderKey(Builder):
    """
    Builder responsible for generating a parameter name.
    """
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(self.expected_sequences())

    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        return (self.context.param_names[0],)

    def next_builder(self) -> Builder:
        return BuilderKVSep(self.context)


class BuilderParameter_start(Builder):
    """
    Builder responsible for generating the opening of the
    parameters object.
    """
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(self.expected_sequences())

    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        return (self.context.param_start, )

    def next_builder(self) -> Builder:
        return BuilderKey(self.context)


class BuilderFunction(Builder):
    """
    Builder responsible for selecting which function should be called.

    The generated function determines the parameter names and types
    used during the remainder of the constrained decoding process.
    """
    def get_allowed(self) -> set[int]:
        return self._valid_tokens(self.expected_sequences())

    def expected_sequences(self) -> tuple[tuple[int, ...], ...]:
        return tuple(self.context.functions.keys())

    def next_builder(self) -> Builder:
        function = self.context.functions[tuple(self.tokens)]
        self.context.param_names = function.param_names.copy()
        self.context.param_types = function.param_types.copy()
        return BuilderParameter_start(self.context)
