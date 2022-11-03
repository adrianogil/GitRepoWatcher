
def get_cmd_flags():
    return ["-l", "--list"]


def get_help_usage_str():
    return "\trepo-watcher -l : list all registered repos\n"


def execute(args, extra_args, controller):
    if len(args) == 0 and len(extra_args) == 1:
        new_extra_args = dict(extra_args)
        new_extra_args['--all'] = []
        extra_args = new_extra_args

    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)
    # repo_list = controller.get_repos()

    index = 0
    for repo in repo_list:
        print('Repo ' + str(index) + ': ' + str(repo.name) + " (ID: " + str(repo.id) + ")")
        print('- path: ' + str(repo.path))
        print('- categories: ')
        for c in repo.categories:
            print('\t- ' + c.name)
        print('- update command: ' + str(repo.update_command))
        index = index + 1
