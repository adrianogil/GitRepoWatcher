import subprocess
import shlex

def get_cmd_flags():
    return ["--exec"]


def get_help_usage_str():
    return "\trepo-watcher --exec <command> [<search args>]: execute a command in all repos"


def execute(args, extra_args, controller):

    # if len(args) == 2:
    #     results = get_repos_from_args([args[0]], extra_args)
    #     command_batch = args[1]
    # elif len(args) == 1:
    #     results = get_repos_from_args([], extra_args)
    #     command_batch = args[0]
    # else:
    #     return

    if len(args) > 0:
        command_batch = args[0]
    else:
        return

    command_args = shlex.split(command_batch)
    if not command_args:
        return

    search_conditions = controller.get_search_conditions(args[1:], extra_args)
    repo_list = controller.get_repos(search_conditions)

    total_commits_in_all_repos = 0
    index = 0

    for repo in repo_list:
        print("###################################################")
        print('Repo %s (Id %s)\n' % (repo.name,repo.id))
        repo_command_output = subprocess.check_output(command_args, cwd=str(repo.path))
        repo_command_output = repo_command_output.decode("utf-8").strip()

        print(repo_command_output)

        index = index + 1
