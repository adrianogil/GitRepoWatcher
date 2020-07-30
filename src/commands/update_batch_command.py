import platform
import subprocess


def execute(args, extra_args, controller):
    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)
    for repo in repo_list:
        try:
            print("###################################################")
            print('Repo ' + str(repo.id) + ': Updating ' + repo.name)
            new_commits = controller.update_gitrepo(repo)
            new_commits = int(new_commits)
            if new_commits > 0:
                notify_new_commits(repo.name, new_commits)
        except Exception as exception:
            print("Got some errors when updated %s repo: %s" % (repo.name, exception))


def is_termux():
    return platform.machine() == "aarch64"


def notify_new_commits(repo_name, new_commits):
    if is_termux():
        pass
    else:
        subprocess_cmd = 'terminal-notifier -title "Repo %s" -message "%s new commits!"' % (
                repo_name,
                new_commits
            )
        subprocess.check_output(subprocess_cmd, shell=True)
