from repowatcher.utils.printlog import printlog


def get_cmd_flags():
    return ["-vc", "--verify-change"]


def get_help_usage_str():
    return "\trepo-watcher -vc : verify which repo has unstaged or uncommited changes \n"


def execute(args, extra_args, controller):
    # if len(args) == 0:
    # category='%'
    # elif len(args) > 0:
    #     category = args[0]

    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    unstaged_repos = []

    index = 0
    for repo in repo_list:
        try:
            unstaged = controller.get_unstaged_files(repo)
            total_commits = controller.get_diverge_commits_to_upstream(repo)

            # try:
            index = index + 1
            printlog("###################################################")
            current_repo = repo.name

            if unstaged != '0':
                printlog('There are unstaged changes in repo!')
                unstaged_repos.append({'id' : repo.id, 'repo' : current_repo, 'unstaged' : unstaged, 'commits': total_commits})
            else:
                if total_commits != '0':
                    printlog('There are commits to be sent to upstream!')
                    unstaged_repos.append({'id' : repo.id, 'repo' : current_repo, 'unstaged' : unstaged, 'commits': total_commits})
        except:
            printlog("Caught error when handling repo " + str(current_repo))
    printlog("###################################################")

    total_unstaged = len(unstaged_repos)
    if total_unstaged == 1:
        printlog("Found changes in only 1 repo:")
    else:
        printlog("Found changes in %s repos:" % (total_unstaged,))
    for u in unstaged_repos:
        printlog("  - (ID: %s) %s - (%s unstaged) (%s commits)" % \
            (u['id'], u['repo'], u['unstaged'], u['commits']))
    printlog("###################################################")