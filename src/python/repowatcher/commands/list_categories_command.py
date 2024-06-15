
def get_cmd_flags():
    return ["-lc", "--list"]


def get_help_usage_str():
    return "\trepo-watcher -lc: list categories"


def execute(args, extra_args, controller):

    categories_list = controller.get_categories()

    index = 0
    for cat in categories_list:
        print('' + str(index) + ': ' + str(cat.name) + " (ID: " + str(cat.id) + ")")
        index = index + 1
