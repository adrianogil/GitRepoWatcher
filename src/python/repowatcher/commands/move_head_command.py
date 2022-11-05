

def get_cmd_flags():
    return ["-up", "--update"]


def get_help_usage_str():
    return "\trepo-watcher -up : for each target repo fetch new commits and move head (in case there is no changes) \n"


def execute(args, extra_args, controller):
    if len(args) == 0:
        category='%'
    elif len(args) > 0:
        category = args[0]

    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    index = 0;
    new_commits = {}

    for repo in repo_list:
        # try:
        index = index + 1
        print("###################################################")
        current_repo = repo.name
        print('Repo ' + str(index) + ': Move HEAD to upstream in ' + current_repo)
        
        diverge_commits = controller.get_diverge_commits_to_upstream(repo)
        unstaged = controller.get_unstaged_files(repo)

        if diverge_commits == '0':
            print('There are no new commits!')
        elif unstaged == '0':
            number_new_commits = diverge_commits
            diverge_commits = controller.get_diverge_commits_from_upstream(repo)

            if diverge_commits == '0':
                move_output = controller.move_to_upstream(repo)
                print(move_output)
                new_commits[repo.name] = number_new_commits
            else:
                print('There are commits to be synced with upstream in repo!')
        else:
            print('There are unstaged changes in repo!')
        # except:
        #     print("Caught error when handling repo " + str(current_repo))

    print("###################################################")
    total_repo_updated = len(new_commits)
    if total_repo_updated == 0:
        print('Not a single repo was updated!')
    else:
        print('' + str(total_repo_updated) + ' repo were updated:')
        for r in new_commits:
            print(' - ' + r + ': ' + new_commits[r] + ' new commits')