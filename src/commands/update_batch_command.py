def execute(args, extra_args, controller):
    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)
    for repo in repo_list:
        print("###################################################")
        print('Repo ' + str(repo.id) + ': Updating ' + repo.name)
        controller.update_gitrepo(repo)