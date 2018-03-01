import subprocess

def get_upstream_name(path):
    get_upstream_name = ' git rev-parse --abbrev-ref --symbolic-full-name @{u}'
    get_upstream_command = 'cd "' + path + '" && ' + get_upstream_name
    upstream = subprocess.check_output(get_upstream_command, shell=True)
    upstream = upstream.strip()

    return upstream

def get_diverge_commits(path):
    upstream = get_upstream_name(path)

    get_diverge_commits = 'git log HEAD..' + upstream + ' --pretty=oneline | wc -l'
    get_diverge_commits_command = 'cd "' + path + '" && ' + get_diverge_commits
    diverge_commits = subprocess.check_output(get_diverge_commits_command, shell=True)
    diverge_commits = diverge_commits.strip()

    return diverge_commits