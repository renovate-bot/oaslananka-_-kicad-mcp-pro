from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import jsonschema
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ICON_SIZES = (16, 32, 48, 64, 128, 256, 512, 1024)
SUBMISSION_DOCS = (
    "README.md",
    "anthropic-directory.md",
    "chatgpt-apps.md",
    "openai-mcp-registry.md",
    "reviewer-test-prompts.md",
    "safety-and-permissions.md",
)
SCREENSHOTS = (
    "01-claude-desktop-quality-gate.png",
    "02-cursor-schematic-build.png",
    "03-vscode-pcb-inspection.png",
    "04-tools-reference.png",
    "05-export-manufacturing.png",
)
FORBIDDEN_NAMESPACE = tuple(
    "".join(parts)
    for parts in (
        ("oaslananka", "-", "lab"),
        ("oaslananka", "_", "lab"),
        ("oaslananka", "/", "lab"),
        ("lab", "/", "oaslananka"),
        ("kicad-mcp-pro", "-", "lab"),
    )
)
RUNNER_PREFIXES = ("ubuntu-", "macos-", "windows-")


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str


def _tool(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        msg = f"{name} not found on PATH"
        raise RuntimeError(msg)
    return executable


def _git_files() -> list[Path]:
    result = subprocess.run(
        [_tool("git"), "ls-files"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        msg = result.stderr.strip() or "git ls-files failed"
        raise RuntimeError(msg)
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _tracked_text_files() -> list[Path]:
    return [path for path in _git_files() if path.is_file()]


def _contains_any(path: Path, needles: tuple[str, ...]) -> list[str]:
    text = _read_text(path)
    return [needle for needle in needles if needle in text]


def _namespace_check() -> CheckResult:
    hits: list[str] = []
    for path in _tracked_text_files():
        found = _contains_any(path, FORBIDDEN_NAMESPACE)
        if found:
            hits.append(f"{path.relative_to(ROOT)}: {', '.join(found)}")
    if hits:
        return CheckResult("namespace regression", "FAIL", "; ".join(hits[:10]))
    return CheckResult("namespace regression", "PASS", "no forbidden owner strings")


def _runner_check() -> CheckResult:
    hits: list[str] = []
    workflow_dir = ROOT / ".github" / "workflows"
    for path in [*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml")]:
        payload = yaml.safe_load(_read_text(path)) or {}
        jobs = payload.get("jobs", {}) if isinstance(payload, dict) else {}
        for job_name, job in jobs.items():
            if not isinstance(job, dict) or "runs-on" not in job:
                continue
            runs_on = job["runs-on"]
            values = runs_on if isinstance(runs_on, list) else [runs_on]
            for value in values:
                text = str(value).strip().strip("'\"")
                if text == "ubuntu-latest" or text.startswith(RUNNER_PREFIXES):
                    hits.append(f"{path.relative_to(ROOT)} job {job_name}: {runs_on!r}")
    if hits:
        return CheckResult("runner regression", "FAIL", "; ".join(hits))
    return CheckResult("runner regression", "PASS", "no GitHub-hosted runner tokens")


def _version_check() -> CheckResult:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    versions = {
        "pyproject.toml": pyproject["project"]["version"],
        "server.json": json.loads((ROOT / "server.json").read_text(encoding="utf-8"))["version"],
        "mcp.json": json.loads((ROOT / "mcp.json").read_text(encoding="utf-8"))["version"],
    }
    init_text = (ROOT / "src" / "kicad_mcp" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', init_text)
    versions["src/kicad_mcp/__init__.py"] = match.group(1) if match else ""
    if len(set(versions.values())) != 1:
        return CheckResult("version metadata sync", "FAIL", json.dumps(versions, sort_keys=True))
    return CheckResult("version metadata sync", "PASS", next(iter(versions.values())))


def _pypi_check() -> CheckResult:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = pyproject["project"]["version"]
    try:
        with urlopen("https://pypi.org/pypi/kicad-mcp-pro/json", timeout=10) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, TimeoutError) as exc:
        return CheckResult("pypi reachability", "WARN", f"offline or unavailable: {exc}")
    releases = payload.get("releases", {})
    if version not in releases:
        return CheckResult(
            "pypi current version",
            "WARN",
            f"{version} is not published yet; expected for in-flight release branches",
        )
    return CheckResult("pypi current version", "PASS", f"{version} is published")


def _privacy_check() -> CheckResult:
    path = ROOT / "docs" / "privacy.md"
    if not path.is_file():
        return CheckResult("privacy policy", "FAIL", "docs/privacy.md missing")
    text = _read_text(path).lower()
    if "data" not in text or "telemetry" not in text:
        return CheckResult("privacy policy", "FAIL", "missing data or telemetry language")
    return CheckResult("privacy policy", "PASS", "privacy.md covers data and telemetry")


def _image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def _icon_check() -> CheckResult:
    errors: list[str] = []
    for size in ICON_SIZES:
        path = ROOT / "docs" / "assets" / f"icon-{size}.png"
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
        elif _image_size(path) != (size, size):
            errors.append(f"{path.relative_to(ROOT)} has {_image_size(path)}")
    if errors:
        return CheckResult("icon assets", "FAIL", "; ".join(errors))
    return CheckResult("icon assets", "PASS", "all icon sizes present")


def _screenshot_check() -> CheckResult:
    errors: list[str] = []
    hash_path = ROOT / "scripts" / "_placeholder_hashes.json"
    placeholders = json.loads(hash_path.read_text(encoding="utf-8")) if hash_path.is_file() else {}
    submission_mode = os.environ.get("SUBMISSION_MODE") == "1"
    for filename in SCREENSHOTS:
        path = ROOT / "docs" / "assets" / "screenshots" / filename
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
            continue
        if _image_size(path) != (1920, 1080):
            errors.append(f"{path.relative_to(ROOT)} has {_image_size(path)}")
            continue
        if submission_mode:
            import hashlib

            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if placeholders.get(filename) == digest:
                errors.append(f"{filename} is still the placeholder")
    if errors:
        return CheckResult("screenshot assets", "FAIL", "; ".join(errors))
    return CheckResult("screenshot assets", "PASS", "all screenshot slots valid")


def _demo_cast_check() -> CheckResult:
    path = ROOT / "docs" / "assets" / "demo.cast"
    gif_path = ROOT / "docs" / "assets" / "demo.gif"
    if not path.is_file():
        return CheckResult("demo cast", "FAIL", "docs/assets/demo.cast missing")
    if not gif_path.is_file():
        return CheckResult("demo cast", "FAIL", "docs/assets/demo.gif missing")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        header = json.loads(lines[0])
        frames = [json.loads(line) for line in lines[1:] if line.strip()]
    except (IndexError, json.JSONDecodeError) as exc:
        return CheckResult("demo cast", "FAIL", str(exc))
    if header.get("version") != 2 or not all(isinstance(frame, list) for frame in frames):
        return CheckResult("demo cast", "FAIL", "invalid asciinema v2 structure")
    return CheckResult("demo cast", "PASS", f"{len(frames)} frames and demo.gif present")


def _submission_docs_check() -> CheckResult:
    errors: list[str] = []
    for filename in SUBMISSION_DOCS:
        path = ROOT / "docs" / "submission" / filename
        if not path.is_file():
            errors.append(f"missing {filename}")
            continue
        line_count = len(path.read_text(encoding="utf-8").splitlines())
        if line_count < 150:
            errors.append(f"{filename} has {line_count} lines")
    if errors:
        return CheckResult("submission docs", "FAIL", "; ".join(errors))
    return CheckResult("submission docs", "PASS", "six files at >=150 lines")


def _reviewer_prompts_check() -> CheckResult:
    path = ROOT / "tests" / "reviewer" / "prompts.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return CheckResult("reviewer prompts", "FAIL", str(exc))
    prompts = payload.get("prompts")
    if not isinstance(prompts, list) or len(prompts) != 5:
        return CheckResult("reviewer prompts", "FAIL", "expected exactly five prompts")
    return CheckResult("reviewer prompts", "PASS", "five prompts")


def _readme_check() -> CheckResult:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    missing = []
    if "docs/assets/demo.gif" not in text:
        missing.append("demo gif")
    if "https://oaslananka.github.io/kicad-mcp-pro/privacy/" not in text:
        missing.append("privacy policy URL")
    if missing:
        return CheckResult("README listing references", "FAIL", ", ".join(missing))
    return CheckResult("README listing references", "PASS", "demo and privacy linked")


def _server_schema_check() -> CheckResult:
    schema_path = ROOT / "scripts" / "schemas" / "server.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
        validator_cls = jsonschema.validators.validator_for(schema)
        validator_cls.check_schema(schema)
        errors = sorted(
            validator_cls(schema).iter_errors(server),
            key=lambda error: list(error.path),
        )
    except (OSError, json.JSONDecodeError, jsonschema.SchemaError) as exc:
        return CheckResult("server schema", "FAIL", str(exc))
    if errors:
        return CheckResult("server schema", "FAIL", errors[0].message)
    return CheckResult("server schema", "PASS", "server.json validates")


def _public_listing_check() -> CheckResult:
    path = ROOT / "PUBLIC_LISTING.md"
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if not path.is_file():
        return CheckResult("public listing", "FAIL", "PUBLIC_LISTING.md missing")
    if "PUBLIC_LISTING.md" not in readme:
        return CheckResult(
            "public listing",
            "FAIL",
            "README.md does not reference PUBLIC_LISTING.md",
        )
    return CheckResult("public listing", "PASS", "root listing file referenced")


def run_checks() -> list[CheckResult]:
    first_namespace = _namespace_check()
    first_runner = _runner_check()
    final_namespace = _namespace_check()
    final_runner = _runner_check()
    final_namespace = CheckResult(
        "namespace regression final pass",
        final_namespace.status,
        final_namespace.detail,
    )
    final_runner = CheckResult(
        "runner regression final pass", final_runner.status, final_runner.detail
    )
    return [
        first_namespace,
        first_runner,
        _version_check(),
        _pypi_check(),
        _privacy_check(),
        _icon_check(),
        _screenshot_check(),
        _demo_cast_check(),
        _submission_docs_check(),
        _reviewer_prompts_check(),
        _readme_check(),
        _server_schema_check(),
        _public_listing_check(),
        final_namespace,
        final_runner,
    ]


def main() -> int:
    results = run_checks()
    print("| Check | Result | Detail |")
    print("|---|---|---|")
    for result in results:
        detail = result.detail.replace("|", "\\|")
        print(f"| {result.name} | {result.status} | {detail} |")
    return 1 if any(result.status == "FAIL" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
