from repowatcher.utils.printlog import printlog


def get_cmd_flags():
    return ["--sync"]


def get_help_usage_str():
    help_usage_str = "\trepo-watcher --sync : for each target repo run git remote update, git rebase and git push\n"
    help_usage_str += "\trepo-watcher --sync <category-list> : run sync pipeline only for repos from the given categories\n"
    return help_usage_str


def execute(args, extra_args, controller):
    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    for index, repo in enumerate(repo_list):
        printlog("###################################################")
        printlog('Repo ' + str(index) + ' - ' + repo.name + ': Syncing repository')

        remote_update_output = controller.remote_update(repo)
        printlog(remote_update_output)

        rebase_result = controller.rebase(repo)
        printlog(rebase_result['output'])

        if not rebase_result['ok?']:
            printlog('Rebase failed for ' + repo.name + '. Aborting rebase and skipping push.')
            abort_output = controller.abort_rebase(repo)
            printlog(abort_output)
            continue

        push_output = controller.push(repo)
        printlog(push_output)

    printlog("###################################################")
