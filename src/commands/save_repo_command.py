import os
import git # pip install gitpython

from subprocess import *

def get_git_root(p):
    """Return None if p is not in a git repo, or the root of the repo if it is"""
    if call(["git", "branch"], stderr=STDOUT, stdout=open(os.devnull, 'w'), cwd=p) != 0:
        return None
    else:
        root = check_output(["git", "rev-parse", "--show-toplevel"], cwd=p)
        return root

def is_git_repo(path):
    try:
        _ = git.Repo(path).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False

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
        return controller.categoryDAO.default_category

def execute(args, extra_args, controller):
    print("save_repo_command.py - " + str(args) + " " + str(extra_args))

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
    
    repo_path = git_repo_path
    repo_name = os.path.basename(repo_path)

    print('Saving repo ' + repo_name)
    print('Identified path ' + repo_path)
    print('Repo Category: ' + str(get_categories_from(extra_args, controller)))
    print('Using update-command as "' +  update_command + '"')

    repo_args = {
        "name"           : repo_name,
        "path"           : repo_path,
        "categories"     : get_categories_from(extra_args, controller),
        "update_command" : repo_name,
    }

    repo = controller.entity_factory.create_repo(repo_args)
    operation_obj = controller.save_repo(repo)

    if operation_obj.success:
        saved_repo = operation_obj.data
        print('Repo saved with ID ' + str(saved_repo.id))
    else:
        print('Error while saving repo.')

    