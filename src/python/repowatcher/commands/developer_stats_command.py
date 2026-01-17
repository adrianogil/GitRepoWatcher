def get_cmd_flags():
    return ["--developer-stats"]


def get_help_usage_str():
    return "\trepo-watcher --developer-stats <developer email> [<search args>]: show developer commit stats\n"


def execute(args, extra_args, controller):
    if len(args) == 0:
        print("Missing developer email.")
        print(get_help_usage_str())
        return

    developer_email = args[0]
    search_conditions = controller.get_search_conditions(args[1:], extra_args)
    repo_list = controller.get_repos(search_conditions)

    total_commits_in_all_repos = 0
    index = 0
    repo_stats = []

    for repo in repo_list:
        try:
            commits = controller.get_commits_by_author(repo, developer_email)
            repo_stats.append((repo, commits))
            total_commits_in_all_repos += commits
        except Exception:
            print("Caught error when handling repo " + str(index))
        index = index + 1

    ordered_repo_list = sorted(repo_stats, key=lambda x: x[1], reverse=True)

    print("Developer stats for " + developer_email)
    for repo, commits in ordered_repo_list:
        print("Repo %s (Id %s) " % (repo.name, repo.id))
        print("  Commits: " + str(commits))

    print("Commits in all repos: " + str(total_commits_in_all_repos))
