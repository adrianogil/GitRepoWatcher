def get_cmd_flags():
    return ["-h", "--help"]


def get_help_usage_str():
    return "\trepo-watcher -h : show this help text\n"


def execute(args, extra_args, controller):
    help_txt = "GitRepoWatcher command.\nUsage:\n"

    for cmd in controller.available_commands:
        help_txt += cmd.get_help_usage_str()

    print(help_txt)
