"""Local workflow lint wrapper."""

from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

import yaml


def _run(command: list[str]) -> None:
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--actionlint", action="store_true", help="Run actionlint as well.")
    args = parser.parse_args()

    workflow_dir = pathlib.Path(".github/workflows")
    for path in sorted(workflow_dir.glob("*.yml")):
        yaml.safe_load(path.read_text(encoding="utf-8"))
    print(f"Parsed {len(list(workflow_dir.glob('*.yml')))} workflow file(s).")

    if args.actionlint:
        binary = shutil.which("actionlint")
        if binary is None:
            print(
                "actionlint is required for workflow linting. Install from "
                "https://github.com/rhysd/actionlint or use the GitHub workflow.",
                file=sys.stderr,
            )
            raise SystemExit(127)
        _run([binary])


if __name__ == "__main__":
    main()
