
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file


def call_function(function_call_part: types.FunctionCall, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    args = function_call_part.args
    args["working_directory"] = "./calculator/"
    functions = {
        "schema_get_files_info": schema_get_files_info,
        "schema_get_file_content": schema_get_file_content,
        "schema_run_python_file": schema_run_python_file,
        "schema_write_file": schema_write_file,
    }
