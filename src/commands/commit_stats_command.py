
def execute(args, extra_args, controller):

    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    total_commits_in_all_repos = 0
    index = 0

    for repo in repo_list:
        print('Repo %s (Id %s) ' % (repo.name,repo.id))
        total_commits = controller.get_total_commits(repo)
        print('  Total commits: ' + str(total_commits))
        total_commits_in_all_repos = total_commits_in_all_repos + total_commits

        index = index + 1
    print('Commits in all repos: ' + str(total_commits_in_all_repos))