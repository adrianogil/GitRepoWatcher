from repowatcher.gitcommands import get_git_root
import os

from repowatcher.utils.printlog import printlog


def get_cmd_flags():
    return ["-s", "--save"]


def get_help_usage_str():
     help_str = "\trepo-watcher -s : register current repo\n"
     help_str += "\trepo-watcher -s -c <category1> <category2>: register current repo with a list of categories\n"
     return help_str


def get_categories_from(extra_args, controller):
    if '-c' in extra_args:
        str_categories = extra_args['-c']

        categories_objs = []

        for c in str_categories:
            cat_obj = controller.categoryDAO.get(c)
            if cat_obj is None:
                cat_obj = controller.categoryDAO.save(c)
            categories_objs.append(cat_obj)

        return categories_objs
    else:
        return [controller.categoryDAO.default_category]


def execute(args, extra_args, controller):
    printlog("save_repo_command.py - " + str(args) + " " + str(extra_args), debug=True)

    if len(args) == 0:
        update_command = 'git remote update'
        category = 'default'
    elif len(args) == 1:
        category = args[0]
        update_command = 'git remote update'
    elif len(args) >= 2:
        update_command = args[0]
        category = args[1]

    repo_path = os.getcwd()

    # Verify if path is a git repo
    git_repo_path = get_git_root(repo_path)
    if git_repo_path is None:
        print(repo_path)
        print('Current path is not a git project')
        return

    repo_path = git_repo_path.strip()
    repo_name = os.path.basename(repo_path)
    repo_categories = get_categories_from(extra_args, controller)

    repo_category_names = []
    for category in repo_categories:
        repo_category_names.append(category.name)

    print('Saving repo %s' % (repo_name,))
    print('Identified path %s' % (repo_path,))
    print('Repo Categories: %s' % (repo_category_names,))
    print('Using update-command as "%s"' % (update_command,))

    repo_args = {
        "name"           : repo_name,
        "path"           : repo_path,
        "categories"     : repo_categories,
        "update_command" : update_command,
    }

    repo = controller.entity_factory.create_repo(repo_args)
    operation_obj = controller.save_repo(repo)

    if operation_obj.success:
        saved_repo = operation_obj.data
        print('Repo saved with ID ' + str(saved_repo.id))
    else:
        print('Error while saving repo.')

    