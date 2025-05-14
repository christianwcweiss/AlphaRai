#!/usr/bin/env python

import sys
import subprocess
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
code_root = repo_root / "code"
code_quant_core = code_root / "quant_core"
code_quant_dev = code_root / "quant_dev"
code_app = code_root / "app"

sys.path.insert(0, str(code_root))
sys.path.insert(0, str(code_quant_core))
sys.path.insert(0, str(code_quant_dev))
sys.path.insert(0, str(code_app))

ignored_in_tests = [
    "W0201",  # attribute-defined-outside-init
    "R0903",  # too-few-public-methods,
    "R0913",  # too-many-arguments
    "R0917",  # too-many-positional-arguments
    "R0914",  # too-many-locals
    "C0115",  # missing-class-docstring
    "C0116",  # missing-function-docstring
    "E0401",  # quant_dev - import-error
    "E0611",  # quant_dev - no-name-in-module
    "W0212",  # protected-access, ignore for tests
]
ignored_globally = [
    "C0114",  # missing-module-docstring
    "C0301",  # line-too-long - managed by Black
    "C0411",
    "C0412",
    "C0413",  # import-ordering - managed by black
    "R0801",  # duplicate-code, disable at some point
    "C0104",  # disallowed-name, doesn't matter
    "W0221",  # arguments-differ, disable at some point
    "C0327",  # mixed-line-endings - managed by black
]

files = sys.argv[1:]
test_files = [f for f in files if f.endswith("_test.py")]
regular_files = [f for f in files if not f.endswith("_test.py")]

base_cmd = [
    "pylint",
    "--init-hook",
    f"import sys; "
    f"sys.path.insert(0, '{code_root.as_posix()}'); "
    f"sys.path.insert(0, '{code_quant_core.as_posix()}'); "
    f"sys.path.insert(0, '{code_quant_dev.as_posix()}'); "
    f"sys.path.insert(0, '{code_app.as_posix()}')",
]


def run(files, disables):
    if not files:
        return 0
    command = base_cmd + [f"--disable={','.join(disables)}"] + files
    return subprocess.call(command)


rc1 = run(test_files, ignored_globally + ignored_in_tests)
rc2 = run(regular_files, ignored_globally)

sys.exit(rc1 or rc2)
