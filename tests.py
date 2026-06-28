#!/usr/bin/env -S uv run --script

from functions.run_python_file import run_python_file
from functions.get_files_info import get_files_info


def test():
    print("\n(should print the calculator's usage instructions)")
    print(run_python_file("calculator", "main.py"))
    print("\n(should run the calculator... which gives a kinda nasty rendered result)")
    print(run_python_file("calculator", "main.py", ["3 + 5"]))
    print("\n()")
    print(run_python_file("calculator", "tests.py"))
    print("\n(this should return an error)")
    print(run_python_file("calculator", "../main.py"))
    print("\n(this should return an error)")
    print(run_python_file("calculator", "nonexistent.py"))
    print("\n(this should return an error)")
    print(run_python_file("calculator", "lorem.txt"))


if __name__ == "__main__":
    test()
