import argparse
import json
import sys
from pathlib import Path
from typing import Any
from pydantic import ValidationError
from .data_model import FunctionDefinition, TestPrompt


def get_arguments() -> Any:
    """
    Parse command-line arguments for the application.

    Returns:
        Any: Parsed command-line arguments containing the paths to the
        input files and the output file.
    """
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

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='data/output/function_calling_results.json',
        required=False,
        help="Path of the output JSON file.")

    return parser.parse_args()


def get_functions_definition(args: Any) -> list[FunctionDefinition]:
    """
    Load and validate the function definitions file.

    The JSON file is parsed and each entry is validated using the
    ``FunctionDefinition`` Pydantic model.

    Args:
        args (Any):
            Parsed command-line arguments containing the path to the
            function definitions file.

    Returns:
        list[FunctionDefinition]:
            A list of validated function definitions.

    Raises:
        FileNotFoundError:
            If the file does not exist.
        PermissionError:
            If the file cannot be accessed.
        json.JSONDecodeError:
            If the JSON file is malformed.
        ValidationError:
            If the JSON structure does not match the expected schema.
    """
    try:
        with open(args.functions_definition, 'r', encoding='utf-8') as file:
            datos_json = json.load(file)
        funciones = [
            FunctionDefinition(**funcion)
            for funcion in datos_json
        ]
        return funciones
    except FileNotFoundError:
        print(f'File ({args.functions_definition}) was not found.')
        sys.exit(1)
    except PermissionError:
        print('Not enough permissions to open file.')
        sys.exit(1)
    except json.JSONDecodeError:
        print('Functions_definition file invalid json.')
        sys.exit(1)
    except ValidationError as e:
        print(f"Invalid data structure: {e}")
        sys.exit(1)


def get_functions_calling_tests(args: Any) -> list[TestPrompt]:
    """
    Load and validate the prompt test file.

    The JSON file is parsed and each prompt is validated using the
    ``TestPrompt`` Pydantic model.

    Args:
        args (Any):
            Parsed command-line arguments containing the path to the
            prompt test file.

    Returns:
        list[TestPrompt]:
            A list of validated prompt objects.

    Raises:
        FileNotFoundError:
            If the file does not exist.
        PermissionError:
            If the file cannot be accessed.
        json.JSONDecodeError:
            If the JSON file is malformed.
        ValidationError:
            If the JSON structure does not match the expected schema.
    """
    try:
        with open(args.input, 'r', encoding='utf-8') as file:
            datos_prompt = json.load(file)
        prompts = [
            TestPrompt(**prompt)
            for prompt in datos_prompt
        ]
        return prompts
    except FileNotFoundError:
        print(f'File ({args.input}) was not found.')
        sys.exit(1)
    except PermissionError:
        print('Not enough permissions to open file.')
        sys.exit(1)
    except json.JSONDecodeError:
        print('Functions_calling_test file invalid json.')
        sys.exit(1)
    except ValidationError as e:
        print(f"Invalid data structure: {e}")
        sys.exit(1)
