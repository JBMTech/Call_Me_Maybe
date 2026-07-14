import argparse
import json
from typing import Any
from pydantic import ValidationError
from .data_model import FunctionDefinition, TestPrompt


def get_arguments():

    parser = argparse.ArgumentParser(
        description='Project 42 called Call_Me_Maybe, created by jabuleje')

    parser.add_argument(
        '-d', '--functions_definition',
        type=argparse.FileType("r"),
        default='data/input/functions_definition.json',
        required=False,
        help="Path of the input functions definitions file.")

    parser.add_argument(
        '-i', '--input',
        type=argparse.FileType("r"),
        default='data/input/function_calling_tests.json',
        required=False,
        help="Path of the input prompts file.")

    # parser.add_argument(
    #     '-o', '--output',
    #     type=str,
    #     default='data/output/function_calling_result.json',
    #     required=False,
    #     help="Path of the output JSON file.")

    return parser.parse_args()


def get_functions_definition(args: Any) -> list[FunctionDefinition]:
    try:
        datos_json = json.load(args.functions_definition)
        funciones = [
            FunctionDefinition(**funcion)
            for funcion in datos_json
        ]
        return funciones
    except ValidationError as e:
        print(f"Invalid: {e}")
    except FileNotFoundError:
        print('File was not found.')
    except json.JSONDecodeError:
        print('Functions_definition file invalid json')
    except PermissionError:
        print('Not enough permissions '
              'to open file.')


def get_functions_calling_tests(args: Any) -> list[TestPrompt]:
    try:
        datos_prompt = json.load(args.input)
        prompts = [
            TestPrompt(**prompt)
            for prompt in datos_prompt
        ]
        return prompts
    except ValidationError as e:
        print(f"Invalid: {e}")
    except FileNotFoundError:
        print('File was not found.')
    except json.JSONDecodeError:
        print('Prompts file invalid json.')
    except PermissionError:
        print('Not enough permissions '
              'to open file.')
