from repowatcher.utils.clitools import run_cmd
from repowatcher.utils.printlog import printlog

import os
import shlex


def get_unstaged_files(repo_path):
    get_unstaged_files = 'git diff --numstat | wc -l'
    get_unstaged_command = 'cd "' + repo_path + '" && ' + get_unstaged_files
    unstaged = run_cmd(get_unstaged_command)

    return unstaged


def get_git_root(p):
    """Return None if p is not in a git repo, or the root of the repo if it is"""
    is_repo_command = f'cd "{p}" && git branch > /dev/null 2>&1'
    is_repo = run_cmd(is_repo_command)

    if is_repo is None:
        return None

    get_root_command = f'cd "{p}" && git rev-parse --show-toplevel'
    root = run_cmd(get_root_command)

    return root


def get_upstream_name(path):
    get_upstream_name = ' git rev-parse --abbrev-ref --symbolic-full-name @{u}'
    get_upstream_command = 'cd "' + path + '" && ' + get_upstream_name
    # print(get_upstream_command)
    upstream = run_cmd(get_upstream_command)

    return upstream


def push_commits_to_upstream(path):
    upstream = get_upstream_name(path)
    upstream = upstream.replace('/', ' ')

    push_commits = 'git push ' + upstream + ''
    push_commits_command = 'cd "' + path + '" && ' + push_commits
    # print(push_commits_command)
    push_commits_output = run_cmd(push_commits_command)

    return push_commits_output


def _run_git_command(path, git_args):
    import subprocess

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

    get_diverge_commits = f"git log {upstream}..HEAD --pretty=oneline | wc -l"
    get_diverge_commits_command = 'cd "' + path + '" && ' + get_diverge_commits
    diverge_commits = run_cmd(get_diverge_commits_command)

    printlog(f"Diverged commits: {diverge_commits}", debug=True)

    return diverge_commits


def get_diverge_commits_upstream_to_HEAD(path):
    upstream = get_upstream_name(path)

    get_diverge_commits = 'git log ' + upstream + '..HEAD --pretty=oneline | wc -l'
    get_diverge_commits_command = 'cd "' + path + '" && ' + get_diverge_commits
    diverge_commits = run_cmd(get_diverge_commits_command)

    return diverge_commits

def get_total_commits(path):

    get_total_commits = 'git log HEAD --pretty=oneline | wc -l'
    get_total_commits_command = 'cd "' + path + '" && ' + get_total_commits
    total_commits = run_cmd(get_total_commits_command)

    if total_commits is None or total_commits == "":
        return 0

    total_commits = int(total_commits)

    return total_commits

def get_today_commits(path):

    get_today_commits = 'git log HEAD --pretty=oneline --since=midnight'
    get_today_commits_command = 'cd "' + path + '" && ' + get_today_commits
    today_commits_output = run_cmd(get_today_commits_command)
    today_commits_list = today_commits_output.split('\n')

    today_commits = []

    for i in range(0, len(today_commits_list)):
        today_commits_list[i] = today_commits_list[i].strip()
        if today_commits_list[i] != "":
            today_commits.append(today_commits_list[i])

    return today_commits


def get_commits_by_author(path, author_email):
    author = shlex.quote(author_email)
    get_author_commits = f"git log --author={author} --pretty=oneline | wc -l"
    get_author_commits_command = 'cd "' + path + '" && ' + get_author_commits
    author_commits = run_cmd(get_author_commits_command).strip()

    if author_commits == "":
        return 0

    return int(author_commits)


def get_last_commit(path):

    get_last_commit = "git log --pretty=format:'%h %ad | %s%d [%an]' --date=short | head -1"
    get_last_commit_command = 'cd "' + path + '" && ' + get_last_commit
    last_commit_output = run_cmd(get_last_commit_command)

    if last_commit_output is None:
        return ""

    return last_commit_output

def get_last_commit_date(path):

    get_last_commit = "git log --pretty=format:'%ad' --date=short | head -1"
    get_last_commit_command = 'cd "' + path + '" && ' + get_last_commit
    last_commit_output = run_cmd(get_last_commit_command)

    if last_commit_output is None:
        return ""

    return last_commit_output
