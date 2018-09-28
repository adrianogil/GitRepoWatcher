def execute(args, extra_args, controller):
    # if len(args) == 0:
    #     category='%'
    # elif len(args) > 0:
    #     category = args[0]

    repo_list = controller.get_repos()
    for repo in repo_list:
        print("###################################################")
        print('Repo ' + str(repo.id) + ': Updating ' + repo.name)
        controller.update_gitrepo(repo)