import subprocess

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

    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    total_commits_in_all_repos = 0
    index = 0

    for repo in repo_list:
        print("###################################################")
        print('Repo %s (Id %s)\n' % (repo.name,repo.id))
        repo_command = 'cd "' + str(repo.path) + '" && ' + command_batch
        repo_command_output = subprocess.check_output(repo_command, shell=True)
        repo_command_output = repo_command_output.strip()

        print(repo_command_output)

        index = index + 1