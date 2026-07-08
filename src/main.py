import argparse
import json
import sys

from pydantic import ValidationError
from .data_model import FunctionDefinition, TestPrompt

def main():
    parser = argparse.ArgumentParser(description='Call_Me_Maybe')
    parser.add_argument('--functions_definition',
                        type=argparse.FileType("r"),
                        required=True,
                        help="Ruta del fichero JSON de Funciones")
    parser.add_argument('--input',
                        type=argparse.FileType("r"),
                        required=True,
                        help="Ruta de fichero de JSON de Prompts")

    args = parser.parse_args()

    try:
        datos_json = json.load(args.functions_definition)
        funciones = [
            FunctionDefinition(**funcion)
            for funcion in datos_json
        ]

        print(f"\nSe han cargado {len(funciones)} funciones.\n")

        for funcion in funciones:
            print(f"Nombre: {funcion.name}")
            print(f"Descripción: {funcion.description}")
            print(f"Parámetros: {list(funcion.parameters.keys())}")
            print(f"Retorno: {funcion.returns}")
            print("-" * 40)

        datos_prompt = json.load(args.input)
        prompts = [
            TestPrompt(**prompt)
            for prompt in datos_prompt
        ]

        print(f"\nSe han cargado {len(prompts)} prompts.\n")

        for line in prompts:
            print(f"Prompt: {line.prompt}")
            print("-" * 40)

    except (ValidationError, json.JSONDecodeError) as e:
        print(e)
    finally:
        if hasattr(args, "functions_definition") and args.functions_definition:
            args.functions_definition.close()
        if hasattr(args, "input") and args.input:
            args.input.close()

    # parser.add_argument('--output', type=str)


if __name__ == "__main__":
    main()
