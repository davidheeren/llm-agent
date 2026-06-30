#!/usr/bin/env -S uv run --script

import os
import sys
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from call_function import get_available_functions, call_function


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
    for _ in range(20):
        if (not run_agent(args, client, messages)):
            return

    print("Error: Model had too many iterations")
    exit(1)


# Return true if should continue the loop
def run_agent(args, client, messages) -> bool:
    response = client.models.generate_content(
        # model="gemini-2.5-flash-lite",
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(system_instruction=get_system_prompt(), tools=[get_available_functions()]),
    )

    for canidate in response.candidates:
        messages.append(canidate.content)

    if args.verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        print(f"User prompt: {args.prompt}")

    if response.function_calls:
        function_results = []
        for func in response.function_calls:
            function_call_result: types.Content = call_function(func, args.verbose)
            if not function_call_result.parts:
                raise Exception("Function call result has no parts")
            if not function_call_result.parts[0].function_response:
                raise Exception("Function call result has no function response")
            if not function_call_result.parts[0].function_response.response:
                raise Exception("Function call result has no function response.response")
            function_results.append(function_call_result.parts[0])
            if (args.verbose):
                print(f"-> {function_call_result.parts[0].function_response.response}")
        messages.append(types.Content(role="user", parts=function_results))
    else:
        print(response.text)
        return False
    return True


if __name__ == "__main__":
    main()
