import os

def get_cmd_flags():
    return ["-i", "--info"]


def get_help_usage_str():
    return "\trepo-watcher -i : get info about the repo in the current path\n"

def execute(args, extra_args, controller):

    search_conditions = controller.get_search_conditions(args, extra_args)

    if len(args) == 0:
        search_conditions['path'] = controller.get_git_root(os.getcwd())

    repo_list = controller.get_repos(search_conditions)

    index = 0
    for repo in repo_list:
        print('Repo ' + str(index) + ': ' + str(repo.name) + " (ID: " + str(repo.id) + ")")
        print('- path: ' + str(repo.path))
        print('- categories: ')
        for c in repo.categories:
            print('--\t' + c.name)
        print('- update command: ' + str(repo.update_command))
        index = index + 1

    if len(repo_list) == 0:
        print('Current path is not saved as a repo.')
