import argparse
import json
from pathlib import Path
from typing import Any
from pydantic import ValidationError
from .data_model import FunctionDefinition, TestPrompt


def get_arguments():

    parser = argparse.ArgumentParser(
        description='Project 42 called Call_Me_Maybe, created by jabuleje')

    parser.add_argument(
        '-d', '--functions_definition',
        type=Path,
        default=Path('data/input/functions_definition.json'),
        required=False,
        help="Path of the input functions definitions file.")

    parser.add_argument(
        '-i', '--input',
        type=Path,
        default=Path('data/input/function_calling_tests.json'),
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
        with open(args.functions_definition, 'r', encoding='utf-8') as file:
            datos_json = json.load(file)
        funciones = [
            FunctionDefinition(**funcion)
            for funcion in datos_json
        ]
        return funciones
    except FileNotFoundError:
        print('File was not found.')
    except PermissionError:
        print('Not enough permissions to open file.')
    except json.JSONDecodeError:
        print('Functions_definition file invalid json.')
    except ValidationError as e:
        print(f"Invalid data structure: {e}")


def get_functions_calling_tests(args: Any) -> list[TestPrompt]:
    try:
        with open(args.input, 'r', encoding='utf-8') as file:
            datos_prompt = json.load(file)
        prompts = [
            TestPrompt(**prompt)
            for prompt in datos_prompt
        ]
        return prompts
    except FileNotFoundError:
        print('File was not found.')
    except PermissionError:
        print('Not enough permissions to open file.')
    except json.JSONDecodeError:
        print('Functions_calling_test file invalid json.')
    except ValidationError as e:
        print(f"Invalid data structure: {e}")
