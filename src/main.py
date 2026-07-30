import json

from pydantic import ValidationError

from pathlib import Path

from .arguments import (
    get_arguments,
    get_functions_definition,
    get_functions_calling_tests,
)

# from .data_model import BuildJSON

from .mind_llm import LLMInterface


def try_cast_int(val):
    if isinstance(val, str):
        try:
            return int(val)
        except ValueError:
            return val
    return val


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

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        result_json = []

        for test in prompts:
            # print("=" * 60)
            # print(f"Prompt:\n{test.prompt}\n")

            generated = interface.generate_json(test.prompt)
            json_text = '{"name":"' + generated
            data = json.loads(json_text)
            result = {
                "prompt": test.prompt,
                "name": data["name"],
                "parameters": {
                    k: try_cast_int(v)
                    for k, v in data["parameters"].items()
                },
            }
            # print(json.dumps(result, indent=4))

            result_json.append(result)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_json, f, indent=4, ensure_ascii=False)

        print(f"\n[INFO] Archivo guardado exitosamente en: {output_path}")

    except ValidationError as e:
        print(f"Invalid: {e}")
    except json.JSONDecodeError:
        print("File invalid JSON")


if __name__ == "__main__":
    main()
