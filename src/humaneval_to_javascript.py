# Authored by Carolyn Anderson, based on script by Arjun Guha.
#
# This script translates problems from the OpenAI HumanEval dataset into JavaScript.
import re
import ast
from typing import List
from generic_translator import main

# We turn multi-line docstrings into single-line comments. This captures the
# start of the line.
DOCSTRING_LINESTART_RE = re.compile("""\n(\s+)""")


class JavaScriptTranslator:

    stop = [ '\nfunction ', '\n/*', '\n//', '\nclass' ] # NOTE(carolyn): My guess

    def __init__(self, file_ext):
        self.file_ext = file_ext

    def translate_prompt(self, name: str, args: List[ast.arg], _returns, description: str) -> str:
        js_description = "//" + re.sub(DOCSTRING_LINESTART_RE, "\n// ", description.strip()) + "\n"
        arg_names = [arg.arg for arg in args]
        arg_list = ", ".join(arg_names)
        return f"{js_description}function {name}({arg_list})"+"{\n"

    def test_suite_prefix_lines(self, entry_point) -> List[str]:
        """
        This code goes at the start of the test suite.
        """
        return [ "const assert = require('node:assert');\n", "", "function test() {",f"  let candidate = {entry_point};" ]

    def test_suite_suffix_lines(self) -> List[str]:
        return ["}", "", "test();"]

    def deep_equality(self, left: str, right: str) -> str:
        """
        All tests are assertions that compare deep equality between left and right.

        Make sure you use the right equality operator for your language. For example,
        == is the wrong operator for Java and OCaml.
        """
        return f"  if (assert.deepEqual({left},{right})" + " {\n    true \n  } else {\n  throw new Error('Failed test!') };"

    def gen_literal(self, c: bool | str | int | float):
        """Translate a literal expression
        c: is the literal value
        """
        if type(c) == bool:
            return "true" if c else "false"
        elif type(c) == str:
            return f'"{c}"'
        elif c is None:
            return "null" # NOTE(carolyn): My guess
        return repr(c)

    def gen_var(self, v: str) -> str:
        """Translate a variable with name v."""
        return v

    def gen_list(self, l: List[str]) -> str:
        return "[" + ", ".join(l) + "]"

    def gen_tuple(self, t: List[str]) -> str:
        return "[" + ", ".join(l) + "]"

    def gen_dict(self, keys: List[str], values: List[str]) -> str:
        return "{" + ", ".join(f"{k}: {v}" for k, v in zip(keys, values)) + "}"

    def gen_call(self, func: str, args: List[str]) -> str:
        """Translate a function call `func(args)`
        A function call f(x, y, z) translates to f(x, y, z)
        """
        return f"{func}(" + ", ".join(args) + ")"


if __name__ == "__main__":
    translator = JavaScriptTranslator("js")
    main(translator)