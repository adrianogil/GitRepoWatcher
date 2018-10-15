import os
import subprocess
from subprocess import *

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
    upstream = subprocess.check_output(get_upstream_command, shell=True)
    upstream = upstream.strip()

    return upstream

def push_commits_to_upstream(path):
    upstream = get_upstream_name(path)
    upstream = upstream.replace('/', ' ')

    push_commits = 'git push ' + upstream + ''
    push_commits_command = 'cd "' + path + '" && ' + push_commits
    # print(push_commits_command)
    push_commits_output = subprocess.check_output(push_commits_command, shell=True)
    push_commits_output = push_commits_output.strip()

    return push_commits_output

def get_diverge_commits_HEAD_to_upstream(path):
    upstream = get_upstream_name(path)

    get_diverge_commits = 'git log HEAD..' + upstream + ' --pretty=oneline | wc -l'
    get_diverge_commits_command = 'cd "' + path + '" && ' + get_diverge_commits
    diverge_commits = subprocess.check_output(get_diverge_commits_command, shell=True)
    diverge_commits = diverge_commits.strip()

    return diverge_commits

def get_diverge_commits_upstream_to_HEAD(path):
    upstream = get_upstream_name(path)

    get_diverge_commits = 'git log ' + upstream + '..HEAD --pretty=oneline | wc -l'
    get_diverge_commits_command = 'cd "' + path + '" && ' + get_diverge_commits
    diverge_commits = subprocess.check_output(get_diverge_commits_command, shell=True)
    diverge_commits = diverge_commits.strip()

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
    today_commits_output = subprocess.check_output(get_today_commits_command, shell=True)
    today_commits_output = today_commits_output.strip()
    today_commits_list = today_commits_output.split('\n')

    today_commits = []

    for i in xrange(0, len(today_commits_list)):
        today_commits_list[i] = today_commits_list[i].strip()
        if today_commits_list[i] != "":
            today_commits.append(today_commits_list[i])


    return today_commits
