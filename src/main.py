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

        interface = LLMInterface("Qwen/Qwen3-0.6B", functions_definition)

        for test in prompts:
            print("=" * 60)
            print(f"Prompt:\n{test.prompt}\n")

            result = interface.generate_json(test.prompt)

            print("JSON generado:")
            print(result)
            print()

    except ValidationError as e:
        print(f"Invalid: {e}")
    except json.JSONDecodeError:
        print("File invalid JSON")


if __name__ == "__main__":
    main()
