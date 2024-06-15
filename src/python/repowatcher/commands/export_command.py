import os
import csv


def get_cmd_flags():
    return ["--export"]


def get_help_usage_str():
    return "\trepo-watcher --export: export"


def execute(args, extra_args, controller):
    print("DEBUG export_command.py - " + str(args) + " " + str(extra_args))

    filename = args[0]
    repo_list = controller.get_repos()

    writer = csv.writer(open(filename, 'w'))
    fields_names = ['RepoId', \
                    'Path',\
                    'UpdateCommand',\
                    'Category'
    ]
    writer.writerow([unicode(s).encode("utf-8") for s in fields_names])

    index = 0
    for repo in repo_list:
        row_data = [repo.id, \
                    repo.path, \
                    repo.update_command, \
                    repo.categories[0].name]
        writer.writerow([unicode(s).encode("utf-8") for s in row_data])
        index = index + 1

