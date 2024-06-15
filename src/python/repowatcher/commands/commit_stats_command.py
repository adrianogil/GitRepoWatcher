
def get_cmd_flags():
    return ["--stats"]


def get_help_usage_str():
    return "\trepo-watcher --stats: show stats"


def execute(args, extra_args, controller):
    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    total_commits_in_all_repos = 0
    index = 0

    ordered_repo_list = sorted(repo_list, key=lambda x: controller.get_total_commits(x), reverse=True)

    for repo in ordered_repo_list:
        try:
            print('Repo %s (Id %s) ' % (repo.name,repo.id))
            total_commits = controller.get_total_commits(repo)
            print('  Total commits: ' + str(total_commits))
            total_commits_in_all_repos = total_commits_in_all_repos + total_commits
        except:
            print("Caught error when handling repo " + str(index))
        index = index + 1

    print('Commits in all repos: ' + str(total_commits_in_all_repos))