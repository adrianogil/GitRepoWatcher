from repowatcher.utils.printlog import printlog


def get_cmd_flags():
    return ["-d", "--delete"]


def get_help_usage_str():
    return "\trepo-watcher -d : delete target repo \n"


def execute(args, extra_args, controller):
    printlog('delete_repo_command - args - ' + str(args) + ' - extra_args - ' +
        str(extra_args), debug=True)
    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)
    printlog('delete_repo_command - repo_list - ' + str(repo_list), debug=True)
    controller.delete_repos(repo_list)
    printlog("The following repos were deleted:")
    for repo in repo_list:
        printlog("\t- " + repo.name + " (ID " + str(repo.id) + ")")
