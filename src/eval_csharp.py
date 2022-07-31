# Authored by Abhinav Jangda based on eval_cpp.py
# Copyright (c) 2022, Roblox Inc and University of Massachusetts Amherst
#
# This script runs the C++ Translated HumanEval programs in datasets/cpp-*
import os
import subprocess
from pathlib import Path

import os
import subprocess
import tempfile
from pathlib import Path
from generic_eval import main

LANG_NAME = "CSharp"
LANG_EXT = ".cs"

#Following files have problems:
#137, 
#22: Any
#148: Elipsis

def eval_script(path: str):
    if ".cs" not in path.name:
        return
    basename = ".".join(str(path).split(".")[:-1])
    binaryname = basename + ".exe"
    build = subprocess.run(["csc", "/d:DEBUG", "-r:System.Numerics.dll", path, f"/out:{binaryname}"], capture_output=True)
    status = None
    returncode = -1
    output = None
    if build.returncode != 0:
        # Well, it's a compile error. May be a type error or
        # something. But, why break the set convention
        status = "SyntaxError"
        returncode = build.returncode
        output = build
        print(output.stdout)
        print(output.stderr)
    else:
        try:
            # Assumes exit-code 0 is all okay
            output = subprocess.run(["mono", binaryname], env={"MONO_TRACE_LISTENER":"Console.Error"}, capture_output=True, timeout=5)
            returncode = output.returncode
            output.stderr = str(output.stderr, "utf-8")
            #mono return 0 even when failing
            fail = "System.Diagnostics.DefaultTraceListener.Fail" in output.stderr
            output.returncode = 1 if fail else 0
            if output.returncode == 0:
                status = "OK"
            else:
                # Well, it's a panic
                status = "Exception"
        except subprocess.TimeoutExpired as exc:
            status = "Timeout"
            output = exc
        os.remove(binaryname)

    if output.stdout is not None:
        output.stdout = output.stdout.decode("utf-8")
    else:
        output.stdout = "None"

    if output.stderr == "":
        output.stderr = "None"

    return {
        "status": status,
        "exit_code": returncode,
        "stdout": output.stdout,
        "stderr": output.stderr,
    }

if __name__ == "__main__":
    main(eval_script, LANG_NAME, LANG_EXT)
