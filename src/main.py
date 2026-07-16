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

        print(f"\nSe han cargado {len(functions_definition)} funciones.\n")
        for funcion in functions_definition:
            print(f"ver -> {funcion}")
            print(f"Nombre: {funcion.name}")
            print(f"Descripción: {funcion.description}")
            print(f"Parámetros: {json.dumps(list(funcion.parameters.keys()))}")
            print(f"Retorno: {json.dumps(funcion.returns)}")
            print("-" * 40)

        # prompts = get_functions_calling_tests(args)

        # print(f"\nSe han cargado {len(prompts)} prompts.\n")

        # for line in prompts:
        #     print(f"Prompt: {line.prompt}")
        #     print("-" * 40)

        # interface = LLMInterface("Qwen/Qwen3-0.6B", functions_definition)
        # for line in prompts:
        #     print(f"Lista de tokens -> {interface.get_tokens(line.prompt)}")
        #     print("-*-" * 19)

        # print("\n")

        # for funcion in functions_definition:
        #     print(f"Nombre: {interface.get_tokens(funcion.name)}")
        #     print(f"Descripción: {interface.get_tokens(funcion.description)}")
        #     print(f"Parámetros: {interface.get_tokens(json.dumps(list(funcion.parameters.keys())))}")
        #     print(f"Retorno: {interface.get_tokens(json.dumps(funcion.returns))}")
        #     print("-*-" * 19)

    except ValidationError as e:
        print(f"Invalid: {e}")
    except json.JSONDecodeError:
        print("File invalid JSON")


if __name__ == "__main__":
    main()
