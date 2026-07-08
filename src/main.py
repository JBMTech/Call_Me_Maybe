import argparse
import json
import sys

from pydantic import ValidationError

# from .data_model import DataObjectJSON


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
    print("Datos cargados correctamente: ")
    print(type(datos_json))

    datos_prompt = json.load(args.input)
    print("Datos cargados correctamente: ")
    print(type(datos_prompt))

except json.JSONDecodeError:
    print("Error: El archivo no tiene un formato JSON valido.")
finally:
    if hasattr(args, "functions_definition") and args.functions_definition:
        args.functions_definition.close()
    if hasattr(args, "input") and args.input:
        args.input.close()

# parser.add_argument('--output', type=str)
