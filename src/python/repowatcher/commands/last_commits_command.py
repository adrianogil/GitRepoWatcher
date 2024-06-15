
def get_cmd_flags():
    return ["-ld", "--last-commits"]


def get_help_usage_str():
    return "\trepo-watcher -ld: list last commits"

def execute(args, extra_args, controller):

    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    total_commits_in_all_repos = 0
    index = 0

    ordered_repo_list = sorted(repo_list, key=lambda x: controller.get_last_commit_date(x), reverse=True)

    for repo in ordered_repo_list:
        try:
            print('Repo %s (Id %s) ' % (repo.name,repo.id))
            last_commit = controller.get_last_commit(repo)
            print('\t' + str(last_commit))
        except:
            print("Caught error when handling repo " + str(index))
        index = index + 1
