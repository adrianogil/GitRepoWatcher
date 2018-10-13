
def execute(args, extra_args, controller):

    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    total_commits_in_all_repos = 0
    index = 0

    for repo in repo_list:
        
        
        today_commits_msgs = controller.get_today_commits(repo)
        total_today_commits = len(today_commits_msgs)
        index = index + 1
        
        if total_today_commits > 0:
            print("###################################################")
            print('Repo %s (Id %s) ' % (repo.name,repo.id))
            total_commits_in_all_repos = total_commits_in_all_repos + total_today_commits
            for c in today_commits_msgs:
                print(c)

    print("###################################################")
    if len(args) == 0:
        print('Today, there were generated %s commits in all repos.' % (total_commits_in_all_repos,))
    else:
        print('Today, there were generated %s commits in repos.' % (total_commits_in_all_repos,))    