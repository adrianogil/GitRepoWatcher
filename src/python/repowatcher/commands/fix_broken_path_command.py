import os

def get_cmd_flags():
    return ["-x", "--fix"]


def get_help_usage_str():
    return "\trepo-watcher -x : fix broken path\n"


def execute(args, extra_args, controller):
    if len(args) == 0 and len(extra_args) == 1:
        new_extra_args = dict(extra_args)
        new_extra_args['--all'] = []
        extra_args = new_extra_args

    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    for repo in repo_list:

        if not os.path.exists(repo.path):
            print('Repo with broken path : ' + str(repo.name))
            print("- ID: " + str(repo.id) + "")
            print('- path: ' + str(repo.path))
            controller.delete_repos([repo])
            print("Repo removed. Please add it again!")
