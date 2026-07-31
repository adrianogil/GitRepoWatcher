import csv
import os


REQUIRED_COLUMNS = ('Path', 'UpdateCommand', 'Category')


def get_cmd_flags():
    return ["--import"]


def get_help_usage_str():
    return "\trepo-watcher --import: import csv file"


def execute(args, extra_args, controller):
    print("DEBUG import_command.py - " + str(args) + " " + str(extra_args))

    filename = args[0]

    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, strict=True)
        missing_columns = [
            column for column in REQUIRED_COLUMNS
            if column not in (reader.fieldnames or [])
        ]
        if missing_columns:
            print('Error: missing required CSV columns: ' + ', '.join(missing_columns))
            return

        next_row_number = 2
        try:
            for row in reader:
                row_number = reader.line_num
                next_row_number = row_number + 1
                missing_values = [column for column in REQUIRED_COLUMNS if row[column] is None]
                if missing_values or None in row:
                    print('Error: malformed CSV row ' + str(row_number))
                    return

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
        except csv.Error as error:
            print('Error: malformed CSV row ' + str(next_row_number) + ': ' + str(error))
