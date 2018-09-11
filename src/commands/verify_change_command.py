import subprocess

def execute(args, extra_args, controller):
    # if len(args) == 0:
    # category='%'
    # elif len(args) > 0:
    #     category = args[0]

    repo_list = controller.get_repos()

    unstaged_repos = []

    index = 0
    for repo in repo_list:
        unstaged = controller.get_unstaged_files(repo)
        total_commits = controller.get_total_commits(repo)

        # try:
        index = index + 1
        print("###################################################")
        current_repo = repo.name

        if unstaged != '0':
            print('There are unstaged changes in repo!')
            unstaged_repos.append({'id' : repo.id, 'repo' : current_repo, 'unstaged' : unstaged, 'commits': total_commits})
        else:
            if total_commits != '0':
                print('There are commits to be sent to upstream!')
                unstaged_repos.append({'id' : repo.id, 'repo' : current_repo, 'unstaged' : unstaged, 'commits': total_commits})
        # except:
            # print("Caught error when handling repo " + str(current_repo))
    print("###################################################")

    total_unstaged = len(unstaged_repos)
    if total_unstaged == 1:
        print("Found changes in only 1 repo:")
    else:
        print("Found changes in %s repos:" % (total_unstaged,))
    for u in unstaged_repos:
        print("  - (ID: %s) %s - (%s unstaged) (%s commits)" % \
            (u['id'], u['repo'], u['unstaged'], u['commits']))
    print("###################################################")