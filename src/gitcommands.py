from pyutils.cli.clitools import run_cmd

import os
import subprocess
from subprocess import *


def get_unstaged_files(repo_path):
    get_unstaged_files = 'git diff --numstat | wc -l'
    get_unstaged_command = 'cd "' + repo_path + '" && ' + get_unstaged_files
    unstaged = run_cmd(get_unstaged_command)

    return unstaged


def get_git_root(p):
    """Return None if p is not in a git repo, or the root of the repo if it is"""
    if call(["git", "branch"], stderr=STDOUT, stdout=open(os.devnull, 'w'), cwd=p) != 0:
        return None
    else:
        root = check_output(["git", "rev-parse", "--show-toplevel"], cwd=p)
        root = root.strip()
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


def get_diverge_commits_HEAD_to_upstream(path):
    upstream = get_upstream_name(path)

    get_diverge_commits = 'git log HEAD..' + upstream + ' --pretty=oneline | wc -l'
    get_diverge_commits_command = 'cd "' + path + '" && ' + get_diverge_commits
    diverge_commits = run_cmd(get_diverge_commits_command)

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
    total_commits = subprocess.check_output(get_total_commits_command, shell=True)
    total_commits = total_commits.strip()

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


def get_last_commit(path):

    get_last_commit = "git log --pretty=format:'%h %ad | %s%d [%an]' --date=short | head -1"
    get_last_commit_command = 'cd "' + path + '" && ' + get_last_commit
    last_commit_output = subprocess.check_output(get_last_commit_command, shell=True)
    last_commit_output = last_commit_output.strip()

    return last_commit_output

def get_last_commit_date(path):

    get_last_commit = "git log --pretty=format:'%ad' --date=short | head -1"
    get_last_commit_command = 'cd "' + path + '" && ' + get_last_commit
    last_commit_output = subprocess.check_output(get_last_commit_command, shell=True)
    last_commit_output = last_commit_output.strip()

    return last_commit_output
