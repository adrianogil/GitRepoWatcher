
def execute(args, extra_args, controller):
    # if len(args) == 0:
    # category='%'
    # elif len(args) > 0:
    #     category = args[0]

    repo_list = controller.get_repos()

    index = 0
    for repo in repo_list:
        print('Repo ' + str(index) + ': ' + str(repo.name) + " (ID: " + str(repo.id) + ")")
        print('- path: ' + str(repo.path))
        print('- categories: ')
        for c in repo.categories:
            print('--\t' + c.name)
        print('- update command: ' + str(repo.update_command))
        index = index + 1