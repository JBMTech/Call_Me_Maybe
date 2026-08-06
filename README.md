*This project has been created as part of the 42 curriculum by jabuleje*

# 🧩 Call Me Maybe

## 📖 Description

**Call Me Maybe** is a project that explores **constrained decoding** for function calling with small Large Language Models (LLMs).

The objective is to generate valid JSON objects representing function calls while preventing the language model from producing invalid or malformed outputs. Instead of allowing the model to freely generate every token, the decoder restricts the set of valid tokens according to the current stage of the JSON structure.

The project implements a state-machine approach, where each state is responsible for generating a specific part of the JSON object (function name, parameter names, separators, parameter values, and the end of the object). This guarantees that the generated output always follows the expected JSON format while still allowing the language model to decide which function to call and which parameter values to generate.

The implementation uses the **Qwen3-0.6B** language model together with a custom constrained decoding algorithm developed in Python. Generated outputs are validated using **Pydantic**, and parameter values are converted to their expected data types according to the function definitions.

---

## 🛠️ Instructions

### 📄 Requirements

* Python 3.10 or newer
* `uv`
* `Qwen3-0.6B`

### ▶️ Installation

Clone the repository and install all required dependencies:

```bash
make install
```

or

```bash
uv sync
```

### ▶️ Running the program

Execute the project using:

```bash
make run
```

or directly with:

```bash
uv run python -m src.main \
    --functions_definition data/input/functions_definition.json \
    --input data/input/function_calling_tests.json \
    --output data/output/function_calling_results.json
```

### ▶️ Other commands

```bash
make help  # Syntax for executing a Python script.

make debug  # Run the Python file with the interactive debugger (pdb).

make clean  # Deletes temporary files and Python caches (__pycache__ and .mypy_cache).

make fclean  # Delete EVERYTHING generated, including .venv and the output directory.

make lint  # Analyze the style of Python code (requires flake8 and mypy).
```

### 🔹 Input files

The program expects two input files:

* `functions_definition.json`: contains the available function definitions, their descriptions, parameter names, and parameter types.
* `function_calling_tests.json`: contains the prompts that will be processed by the language model.

### 🔹 Output

The generated function calls are written to:

```text
data/output/function_calling_results.json
```

Each generated object contains:

* the original prompt,
* the selected function name,
* the generated parameters,
* parameter values converted to their corresponding Python types whenever applicable.

## 🧠 Algorithm Explanation

The project implements **constrained decoding** to generate structured JSON function calls using a small language model.

Instead of allowing the model to generate any token from its vocabulary, the decoder restricts the set of valid tokens according to the current stage of the JSON structure. The generation process is implemented as a finite-state machine, where each state is represented by a dedicated `Builder` class.

The decoding process follows these steps:

1. The prompt and the descriptions of all available functions are encoded and provided as the model context.
2. The decoder starts in the `BuilderFunction` state, where only valid function names can be generated.
3. Once a function has been selected, the corresponding parameter names and parameter types are loaded from the function definition.
4. The decoder generates the JSON structure by moving through different states:

   * `BuilderFunction`
   * `BuilderParameter_start`
   * `BuilderKey`
   * `BuilderKVSep`
   * `BuilderValue`
   * `BuilderSep`
   * `BuilderEnd`

5. Structural elements of the JSON (keys, separators and delimiters) are generated using constrained decoding.
6. Parameter values are generated with unrestricted decoding so that the language model can freely produce the requested content.
7. After each generated token, the decoder verifies whether the generated value is still valid JSON. When the beginning of the next JSON field is detected, only the valid portion of the value is kept, and the decoder transitions to the next state.
8. Once all parameters have been generated, the decoder emits the closing JSON tokens and terminates.

This approach guarantees that the overall JSON structure is always valid while preserving the language model's flexibility when generating parameter values.

---

## ♦️ Design Decisions

Several design choices were made during the implementation:

* **State-machine architecture:** Each stage of JSON generation is implemented as an independent `Builder` class. This keeps the decoding logic modular and easy to extend.

* **Constrained decoding for JSON structure:** JSON syntax is generated using predefined token sequences, preventing malformed outputs.

* **Unrestricted decoding for parameter values:** Restricting parameter values too aggressively reduced the model's ability to generate correct answers. Allowing unrestricted generation produced significantly better results.

* **Automatic value truncation:** Generated values are validated continuously. If the model starts generating the next JSON field, only the valid portion of the value is preserved.

* **Pydantic validation:** Generated outputs are validated using Pydantic models before being written to the output file.

* **Type conversion:** Parameter values are converted to their expected Python types according to the function definitions.

---

## ♦️ Performance Analysis

### Accuracy

The constrained decoder consistently produces syntactically valid JSON objects. Compared to unrestricted generation, malformed JSON outputs were eliminated.

The addition of function descriptions to the model context also improved function selection for many prompts.

### Speed

The decoding process performs one inference per generated token. Since only a subset of the vocabulary is considered for structural elements, token selection remains efficient.

Additional optimizations include:

* caching reusable encoded sequences,
* reusing the function description context,
* validating values incrementally instead of reparsing the entire JSON.

### Reliability

The decoder always produces JSON objects with the expected structure.

Pydantic validation ensures that the generated objects conform to the expected schema before they are written to disk.

---

## Challenges Faced

Several implementation challenges were encountered during development.

Initially, parameter generation stopped after the first generated token because `BuilderValue` considered the value complete immediately. This prevented multi-token values such as long numbers or strings from being generated correctly.

A second issue appeared when unrestricted generation caused duplicated parameter values. This was solved by validating the generated value after each token and removing the portion that belonged to the following JSON field.

Another challenge was balancing constrained and unrestricted decoding. Restricting every generated token produced poor semantic results, while allowing unrestricted generation for parameter values significantly improved output quality without sacrificing JSON validity.

Finally, selecting the correct function using a small language model proved difficult for semantically similar prompts. Adding function descriptions to the model context improved this behaviour.

---

## Testing Strategy

The implementation was validated using the provided function-calling test set.

The following aspects were verified:

* correct function selection,
* generation of valid JSON,
* generation of multiple parameter types,
* handling of single-token and multi-token values,
* correct transition between decoding states,
* correct completion of JSON objects,
* validation using Pydantic models,
* automatic conversion of parameter values to their expected Python types.

Additional manual tests were performed using prompts containing:

* integers,
* floating-point numbers,
* negative numbers,
* strings,
* regular expressions,
* boolean values,
* multiple function definitions.

---

## Example Usage

Run the project using:

```bash
make run
```

or

```bash
uv run python -m src.main \
    --functions_definition data/input/functions_definition.json \
    --input data/input/function_calling_tests.json \
    --output data/output/function_calling_results.json
```

Example prompt:

```text
What is the sum of 265 and 345?
```

Generated output:

```json
{
    "prompt": "What is the sum of 265 and 345?",
    "name": "fn_add_numbers",
    "parameters": {
        "a": 265,
        "b": 345
    }
}
```

## 📚 Resources

The following resources were used throughout the development of this project:

### Official documentation

* [Python Documentation](https://docs.python.org/3/)
* [Function calling openai](https://developers.openai.com/api/docs/guides/function-calling)
* [Function calling jacar](https://jacar.es/openai-function-calling/)
* [Python + AI: Tool Calling](https://www.youtube.com/watch?v=a1rfEQnHkm8&t=472s)
* [Python + IA: Recursos](https://github.com/orgs/microsoft-foundry/discussions/165)
* [Técnicas de prompt engineering](https://www.ibm.com/es-es/think/topics/prompt-engineering-techniques#7281536)

### Learning resources

The following topics were studied during the implementation of this project:

* Constrained decoding techniques
* Function calling with Large Language Models
* State machines for structured text generation
* JSON validation and parsing
* Tokenization and autoregressive language models
* Pydantic data validation

### 🤖 Use of Artificial Intelligence

Artificial Intelligence **[ChatGPT]** was used as a development and learning assistant throughout the project.

Its use included:

* Explaining concepts related to constrained decoding and structured generation.
* Discussing alternative implementation approaches.
* Reviewing algorithms and identifying possible bugs.
* Helping understand Python language features and standard library functions.
* Assisting with debugging and analysing unexpected behaviours.
