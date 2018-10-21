import os

def execute(args, extra_args, controller):
    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)
    controller.delete_repos(repo_list)