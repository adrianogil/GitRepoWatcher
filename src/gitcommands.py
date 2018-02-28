import subprocess

def get_upstream_name(path):
    get_upstream_name = ' git rev-parse --abbrev-ref --symbolic-full-name @{u}'
    get_upstream_command = 'cd "' + path + '" && ' + get_upstream_name
    upstream = subprocess.check_output(get_upstream_command, shell=True)
    upstream = upstream.strip()

    return upstream