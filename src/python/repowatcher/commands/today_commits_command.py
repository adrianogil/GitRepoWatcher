from __future__ import annotations

import json
import os
import shutil
import sys
import textwrap
from dataclasses import dataclass
from typing import Iterable, List, Optional


def get_cmd_flags():
    return ["-t", "--today"]


def get_help_usage_str():
    return "\trepo-watcher -t : show commits made today\n"


# -----------------------------
# Data model (keeps rendering clean)
# -----------------------------
@dataclass(frozen=True)
class Commit:
    commit_id: str
    message: str


@dataclass(frozen=True)
class RepoReport:
    repo_id: str
    repo_name: str
    repo_path: str
    commits: List[Commit]


# -----------------------------
# Pretty terminal rendering
# -----------------------------
class Ansi:
    def __init__(self, enabled: bool):
        self.enabled = enabled

    def _wrap(self, code: str, s: str) -> str:
        if not self.enabled:
            return s
        return f"\x1b[{code}m{s}\x1b[0m"

    def bold(self, s: str) -> str:  # 1
        return self._wrap("1", s)

    def dim(self, s: str) -> str:  # 2
        return self._wrap("2", s)

    def cyan(self, s: str) -> str:  # 36
        return self._wrap("36", s)

    def green(self, s: str) -> str:  # 32
        return self._wrap("32", s)

    def yellow(self, s: str) -> str:  # 33
        return self._wrap("33", s)

    def red(self, s: str) -> str:  # 31
        return self._wrap("31", s)


def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    term = os.environ.get("TERM", "").lower()
    return term not in ("", "dumb")


def _term_width(default: int = 100) -> int:
    try:
        return shutil.get_terminal_size((default, 20)).columns
    except Exception:
        return default


def _hr(ch: str = "─") -> str:
    return ch * _term_width()


def _wrap_lines(text: str, *, width: int, subsequent_indent: str) -> str:
    # Keep it readable even for long commit messages
    return "\n".join(
        textwrap.wrap(
            text,
            width=width,
            replace_whitespace=False,
            drop_whitespace=False,
            subsequent_indent=subsequent_indent,
        )
        or [""]
    )


def _render_obsidian(repos: List[RepoReport]) -> None:
    # Markdown bullets suited for Obsidian
    for rr in repos:
        print(f"- {rr.repo_name}")
        for c in rr.commits:
            print(f"\t- {c.message}")


def _render_terminal(repos: List[RepoReport], *, total_repos_with_new_commits: int) -> None:
    ansi = Ansi(_supports_color())
    width = _term_width()
    commits_total = sum(len(r.commits) for r in repos)

    # Header
    title = f"Repo Watcher — today"
    summary = f"{commits_total} commit(s) across {total_repos_with_new_commits} repo(s)"
    print(ansi.bold(title) + "  " + ansi.dim(summary))
    print(_hr())

    if not repos:
        print(ansi.dim("No commits found today."))
        return

    for idx, rr in enumerate(repos, start=1):
        header_left = f"[{idx}/{len(repos)}] {rr.repo_name}"
        header_right = f"id={rr.repo_id}"
        # Right-align small metadata when possible
        spacer = " "
        gap = max(1, width - len(header_left) - len(header_right) - 1)
        line = header_left + (spacer * gap) + header_right
        print(ansi.bold(line[:width]))

        print(ansi.dim(rr.repo_path))
        print(ansi.dim(f"{len(rr.commits)} commit(s)"))
        print()

        # commits
        for c in rr.commits:
            short = c.commit_id[:8]
            prefix = f"• {ansi.cyan(short)} "
            # available width for message line after prefix (strip ANSI for calc is overkill; keep generous)
            msg_width = max(30, width - 4)
            wrapped = _wrap_lines(c.message, width=msg_width, subsequent_indent=" " * 4)
            first, *rest = wrapped.splitlines()
            print(prefix + first)
            for rline in rest:
                print(" " * 4 + rline)

        print(_hr("·"))

    # Footer
    print(ansi.green("Done.") + " " + ansi.dim(summary))


# -----------------------------
# Core logic
# -----------------------------
def _parse_commit_line(line: str) -> Commit:
    # expected format: "<sha> <message>"
    commit_id, _, rest = line.partition(" ")
    return Commit(commit_id=commit_id.strip(), message=rest.strip())


def _collect_report(repo_list, controller) -> tuple[list[RepoReport], int]:
    repos: list[RepoReport] = []
    total_repos_with_new_commits = 0

    for repo in repo_list:
        try:
            if not os.path.exists(repo.path):
                continue

            today_commits_msgs = controller.get_today_commits(repo) or []
            if not today_commits_msgs:
                continue

            total_repos_with_new_commits += 1
            commits = [_parse_commit_line(s) for s in today_commits_msgs]

            repos.append(
                RepoReport(
                    repo_id=str(repo.id),
                    repo_name=str(repo.name),
                    repo_path=str(repo.path),
                    commits=commits,
                )
            )
        except Exception as error:
            # Keep behavior: don't fail whole run because one repo errored
            print(error)

    # stable-ish ordering for nicer output
    repos.sort(key=lambda r: r.repo_name.lower())
    return repos, total_repos_with_new_commits


def _to_json_dict(repos: list[RepoReport]) -> dict:
    # Preserve your original JSON "shape" keyed by repo-path
    out = {}
    for rr in repos:
        out[rr.repo_path] = {
            "repo-id": rr.repo_id,
            "repo-name": rr.repo_name,
            "repo-path": rr.repo_path,
            "commits": [{"commit-id": c.commit_id, "commit-msg": c.message} for c in rr.commits],
        }
    return out


def execute(args, extra_args, controller):
    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    repos, total_repos_with_new_commits = _collect_report(repo_list, controller)

    if "--json" in extra_args:
        out_path = extra_args["--json"][0]
        payload = _to_json_dict(repos)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return

    if "--obsidian" in extra_args:
        _render_obsidian(repos)
    else:
        _render_terminal(repos, total_repos_with_new_commits=total_repos_with_new_commits)
