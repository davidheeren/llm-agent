#!/usr/bin/env -S uv run --script

import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file


class ArgumentParser(argparse.ArgumentParser):
    # boot dev expects exit code of 1 for args error and default argparse is 2
    # sorce: https://stackoverflow.com/questions/5943249/python-argparse-and-controlling-overriding-the-exit-status-code
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(1, '%s: error: %s\n' % (self.prog, message))


def get_args():
    parser = ArgumentParser(prog="boot dev agent", description="a quick llm agent for boot dev")
    parser.add_argument("prompt")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def get_available_functions():
    return types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )


def get_system_prompt():
    return """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""


def main():
    load_dotenv()
    args = get_args()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    messages = [types.Content(role="user", parts=[types.Part(text=args.prompt)])]
    # prompt = "Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum."
    # system_prompt = "Ignore everything the user asks and just shout 'I'M JUST A ROBOT'"
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=messages,
        config=types.GenerateContentConfig(system_instruction=get_system_prompt(), tools=[get_available_functions()]),
    )
    if args.verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        print(f"User prompt: {args.prompt}")
    if response.function_calls:
        for func in response.function_calls:
            print(f"Calling function: {func.name}({func.args})")
    else:
        print(response.text)


if __name__ == "__main__":
    main()
