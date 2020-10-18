import os

def execute(args, extra_args, controller):
    print('DEBUG - delete_repo_command - args - ' + str(args) + ' - extra_args - ' + \
        str(extra_args))
    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)
    print('DEBUG - delete_repo_command - repo_list - ' + str(repo_list))
    controller.delete_repos(repo_list)