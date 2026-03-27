import os


def get_cmd_flags():
    return ["-ss"]


def get_help_usage_str():
    help_str = "\trepo-watcher -ss: register all git repos in subdirectories\n"
    help_str += "\trepo-watcher -ss <category1> <category2>: register all git repos in subdirectories with categories\n"
    return help_str


def _get_categories(category_names, controller):
    if not category_names:
        return [controller.categoryDAO.default_category]

    categories = []
    for category_name in category_names:
        category = controller.categoryDAO.get(category_name)
        if category is None:
            category = controller.categoryDAO.save(category_name)
        categories.append(category)

    return categories


def _find_git_repos_under(base_path):
    git_repo_paths = []

    for root, dirs, _ in os.walk(base_path):
        if root == base_path:
            continue

        git_metadata_path = os.path.join(root, ".git")
        if os.path.isdir(git_metadata_path) or os.path.isfile(git_metadata_path):
            git_repo_paths.append(root)

            if ".git" in dirs:
                dirs.remove(".git")

    return git_repo_paths


def execute(args, extra_args, controller):
    del extra_args

    current_path = os.getcwd()
    repo_paths = _find_git_repos_under(current_path)
    repo_categories = _get_categories(args, controller)

    saved_paths = []
    for repo_path in repo_paths:
        normalized_path = os.path.abspath(repo_path)
        repo_name = os.path.basename(normalized_path)

        existing_repos = controller.get_repos({"path": normalized_path})
        already_saved = False
        for existing_repo in existing_repos:
            existing_repo_path = os.path.abspath(existing_repo.path)
            if existing_repo_path == normalized_path:
                already_saved = True
                break

        if already_saved:
            continue

        repo_args = {
            "name": repo_name,
            "path": normalized_path,
            "categories": repo_categories,
            "update_command": "git remote update",
        }

        repo = controller.entity_factory.create_repo(repo_args)
        operation_obj = controller.save_repo(repo)

        if operation_obj.success:
            saved_paths.append(normalized_path)

    if len(saved_paths) == 0:
        print("No repositories were saved")
    else:
        for saved_path in saved_paths:
            print(saved_path)
