import json

from pydantic import ValidationError

from .arguments import (
    get_arguments,
    get_functions_definition,
    get_functions_calling_tests,
)

from .mind_llm import LLMInterface


def main() -> None:
    try:
        args = get_arguments()
    except Exception as ex:
        print(f'Invalid arguments. Please use --help to get help.'
              f' ({ex})')
        exit(1)

    try:
        functions_definition = get_functions_definition(args)

        prompts = get_functions_calling_tests(args)

        print(f"\nSe han cargado {len(prompts)} prompts.\n")

        interface = LLMInterface("Qwen/Qwen3-0.6B", functions_definition)

    except ValidationError as e:
        print(f"Invalid: {e}")
    except json.JSONDecodeError:
        print("File invalid JSON")


if __name__ == "__main__":
    main()
