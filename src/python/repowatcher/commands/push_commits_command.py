from repowatcher.utils.printlog import printlog


def get_cmd_flags():
    return ["-p", "--push"]


def get_help_usage_str():
    help_usage_str = "\trepo-watcher -p : for each target repo push commits to upstream \n"
    help_usage_str += "\trepo-watcher --push : for each target repo push commits to upstream \n"
    return help_usage_str


def execute(args, extra_args, controller):
    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    index = 0
    for repo in repo_list:
        try:
            results = controller.push_commits_to_upstream(repo)

            if results['ok?']:
                printlog("###################################################")
                printlog('Repo ' + str(index) + ' - ' + repo.name + ': Sending ' +
                    str(results['commits']) + ' commits\n')
                printlog(results['output'] + "\n")
        except:
            printlog("Caught error when handling repo " + str(repo.name))
        index = index + 1
    printlog("###################################################")
