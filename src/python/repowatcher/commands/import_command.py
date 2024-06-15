import csv
import os

def get_cmd_flags():
    return ["--import"]


def get_help_usage_str():
    return "\trepo-watcher --import: import csv file"


def execute(args, extra_args, controller):
    print("DEBUG import_command.py - " + str(args) + " " + str(extra_args))

    filename = args[0]

    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repo_path = row['Path']

            # Verify if path is a git repo
            git_repo_path = controller.get_git_root(repo_path)
            if git_repo_path is None:
                print(repo_path)
                print('Current path is not a git project')
                return

            repo_path = git_repo_path
            repo_name = os.path.basename(repo_path)

            update_command = row['UpdateCommand']

            category = controller.get_category(row['Category'])

            print('Saving repo ' + repo_name)
            print('Identified path ' + repo_path)
            print('Repo Category: ' + category.name + " (" + str(category.id) + ")")
            print('Using update-command as "' +  update_command + '"')

            repo_args = {
                "name"           : repo_name,
                "path"           : repo_path,
                "categories"     : [category],
                "update_command" : update_command,
            }

            repo = controller.entity_factory.create_repo(repo_args)
            operation_obj = controller.save_repo(repo)

            if operation_obj.success:
                saved_repo = operation_obj.data
                print('Repo saved with ID ' + str(saved_repo.id))
            else:
                print('Error while saving repo.')



