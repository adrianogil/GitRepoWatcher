
def get_cmd_flags():
    return ["-pc", "--push"]


def get_help_usage_str():
    return "\trepo-watcher -pc : for each target repo push commits to upstream \n"


def execute(args, extra_args, controller):
    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    index = 0
    for repo in repo_list:
        try:
            results = controller.push_commits_to_upstream(repo)

            if results['ok?']:
                print("###################################################")
                print('Repo ' + str(index) + ' - ' + repo.name + ': Sending ' + \
                    str(results['commits']) + ' commits\n')
                print(results['output'] + "\n")
        except:
            print("Caught error when handling repo " + str(repo.name))
        index = index + 1
    print("###################################################")
