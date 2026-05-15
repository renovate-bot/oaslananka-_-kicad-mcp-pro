from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from urllib.parse import quote

DEFAULT_REPO = "oaslananka/kicad-mcp-pro"
PROTECTED_BRANCHES = {"main", "master", "develop", "gh-pages"}
PROTECTED_PREFIXES = ("release/", "hotfix/")


@dataclass(frozen=True)
class StaleBranch:
    name: str
    last_commit: str


def _run_gh(args: list[str]) -> subprocess.CompletedProcess[str]:
    gh_exe = shutil.which("gh")
    if gh_exe is None:
        raise RuntimeError("gh CLI not found on PATH")
    return subprocess.run([gh_exe, *args], text=True, capture_output=True, check=False)


def _require_gh(args: list[str]) -> str:
    result = _run_gh(args)
    if result.returncode != 0:
        stderr = result.stderr.strip() or "gh command failed"
        raise RuntimeError(stderr)
    return result.stdout


def _candidate_branch(name: str) -> bool:
    return name not in PROTECTED_BRANCHES and not name.startswith(PROTECTED_PREFIXES)


def _parse_iso(value: str) -> datetime:
    normalized = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def find_stale_branches(repo: str, days: int) -> list[StaleBranch]:
    branch_output = _require_gh(
        ["api", "-X", "GET", f"/repos/{repo}/branches?per_page=100", "--jq", ".[].name"]
    )
    cutoff = datetime.now(UTC) - timedelta(days=days)
    stale: list[StaleBranch] = []

    for branch in (line.strip() for line in branch_output.splitlines()):
        if not branch or not _candidate_branch(branch):
            continue

        pr_count_text = _require_gh(
            [
                "pr",
                "list",
                "--repo",
                repo,
                "--head",
                branch,
                "--state",
                "open",
                "--json",
                "number",
                "--jq",
                "length",
            ]
        ).strip()
        if int(pr_count_text or "0") > 0:
            continue

        encoded_branch = quote(branch, safe="")
        branch_sha = _run_gh(
            ["api", f"/repos/{repo}/branches/{encoded_branch}", "--jq", ".commit.sha"]
        )
        if branch_sha.returncode != 0:
            continue

        commit_date = _run_gh(
            [
                "api",
                f"/repos/{repo}/commits/{branch_sha.stdout.strip()}",
                "--jq",
                ".commit.committer.date",
            ]
        )
        if commit_date.returncode != 0:
            continue

        last_commit = commit_date.stdout.strip()
        if last_commit and _parse_iso(last_commit) < cutoff:
            stale.append(StaleBranch(name=branch, last_commit=last_commit))

    return stale


def _old_prs(repo: str) -> str:
    result = _run_gh(
        [
            "pr",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,updatedAt,author",
            "--jq",
            (
                ".[] | select(.updatedAt < (now - 60*86400 | todate)) | "
                '"- #\\(.number) \\(.title) - last: \\(.updatedAt) by @\\(.author.login)"'
            ),
        ]
    )
    if result.returncode != 0:
        return f"unable to list old PRs: {result.stderr.strip()}"
    return result.stdout.strip()


def render_report(repo: str, days: int) -> tuple[str, int]:
    stale = find_stale_branches(repo, days)
    lines = [
        f"# Branch hygiene report - {datetime.now(UTC).date().isoformat()}",
        "",
        f"## Branches older than {days} days without open PRs",
    ]

    if stale:
        lines.extend(f"- `{branch.name}` (last commit: {branch.last_commit})" for branch in stale)
    else:
        lines.append("no stale branches found")

    lines.extend(["", "## Open PRs older than 60 days"])
    old_prs = _old_prs(repo)
    lines.append(old_prs if old_prs else "no old open PRs found")
    return "\n".join(lines) + "\n", len(stale)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a branch hygiene report.")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Exit 1 when the stale branch section has no matches, preserving old "
            "grep-pipeline behavior."
        ),
    )
    args = parser.parse_args(argv)

    try:
        report, stale_count = render_report(args.repo, args.days)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(report, end="")
    if args.strict and stale_count == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
