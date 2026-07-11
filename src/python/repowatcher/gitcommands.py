from repowatcher.utils.printlog import printlog

import os
import shlex
import subprocess


def _decode_output(output):
    if isinstance(output, bytes):
        return output.decode("utf-8").strip()
    return str(output).strip()


def run_command(path, command_args):
    return _decode_output(subprocess.check_output(command_args, cwd=path))


def run_command_string(path, command):
    return run_command(path, shlex.split(command))


def get_unstaged_files(repo_path):
    output = run_command(repo_path, ["git", "diff", "--numstat"])
    return str(len([line for line in output.splitlines() if line.strip()]))


def get_git_root(p):
    """Return None if p is not in a git repo, or the root of the repo if it is"""
    with open(os.devnull, "w") as devnull:
        is_repo = subprocess.call(["git", "branch"], cwd=p, stdout=devnull, stderr=devnull)

    if is_repo != 0:
        return None

    return run_command(p, ["git", "rev-parse", "--show-toplevel"])


def get_upstream_name(path):
    return run_command(path, ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])


def push_commits_to_upstream(path):
    upstream = get_upstream_name(path)
    remote, branch = upstream.split("/", 1)
    return run_command(path, ["git", "push", remote, branch])


def _run_git_command(path, git_args):
    process = subprocess.run(
        ["git"] + git_args,
        cwd=path,
        capture_output=True,
        text=True,
    )

    stdout = (process.stdout or "").strip()
    stderr = (process.stderr or "").strip()
    output = "\n".join([part for part in [stdout, stderr] if part]).strip()

    return {
        "ok?": process.returncode == 0,
        "output": output,
        "returncode": process.returncode,
    }


def remote_update(path):
    result = _run_git_command(path, ["remote", "update"])
    return result["output"]


def rebase(path):
    return _run_git_command(path, ["rebase"])


def abort_rebase(path):
    result = _run_git_command(path, ["rebase", "--abort"])
    return result["output"]


def push(path):
    result = _run_git_command(path, ["push"])
    return result["output"]


def get_diverge_commits_HEAD_to_upstream(path):
    upstream = get_upstream_name(path)

    printlog(f"Found the upstream name: {upstream}", debug=True)

    diverge_commits = _count_log_commits(path, [f"{upstream}..HEAD"])

    printlog(f"Diverged commits: {diverge_commits}", debug=True)

    return diverge_commits


def get_diverge_commits_upstream_to_HEAD(path):
    upstream = get_upstream_name(path)

    diverge_commits = _count_log_commits(path, [upstream + '..HEAD'])

    return diverge_commits


def _count_log_commits(path, rev_args):
    output = run_command(path, ["git", "log"] + rev_args + ["--pretty=oneline"])
    return str(len([line for line in output.splitlines() if line.strip()]))


def get_total_commits(path):
    total_commits = _count_log_commits(path, ["HEAD"])
    return int(total_commits)

def get_today_commits(path):
    today_commits_output = run_command(path, ["git", "log", "HEAD", "--pretty=oneline", "--since=midnight"])
    today_commits_list = today_commits_output.split('\n')

    today_commits = []

    for i in range(0, len(today_commits_list)):
        today_commits_list[i] = today_commits_list[i].strip()
        if today_commits_list[i] != "":
            today_commits.append(today_commits_list[i])

    return today_commits


def get_commits_by_author(path, author_email):
    author_commits = _count_log_commits(path, ["--author=" + author_email])

    if author_commits == "":
        return 0

    return int(author_commits)


def get_last_commit(path):
    last_commit_output = run_command(path, ["git", "log", "--pretty=format:%h %ad | %s%d [%an]", "--date=short", "-1"])

    if last_commit_output is None:
        return ""

    return last_commit_output

def get_last_commit_date(path):
    last_commit_output = run_command(path, ["git", "log", "--pretty=format:%ad", "--date=short", "-1"])

    if last_commit_output is None:
        return ""

    return last_commit_output
