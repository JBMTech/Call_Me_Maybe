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
            print(f"Nombre: {funcion.name}")
            print(f"Descripción: {funcion.description}")
            print(f"Parámetros: {list(funcion.parameters.keys())}")
            print(f"Retorno: {funcion.returns}")
            print("-" * 40)

        prompts = get_functions_calling_tests(args)

        print(f"\nSe han cargado {len(prompts)} prompts.\n")

        for line in prompts:
            print(f"Prompt: {line.prompt}")
            print("-" * 40)

        # interface = LLMInterface("Qwen/Qwen3-0.6B")
        # print(f"Modelo cargado correctamente {interface.model_name}")

    except (ValidationError, json.JSONDecodeError) as e:
        print(f"Invalid: {e}")


if __name__ == "__main__":
    main()
