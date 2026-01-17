def get_cmd_flags():
    return ["-h", "--help"]


def get_help_usage_str():
    return "\trepo-watcher -h : show this help text\n"


def execute(args, extra_args, controller):
    help_txt = "GitRepoWatcher command.\nUsage:\n"

    for cmd in controller.available_commands:
        command_help_str = cmd.get_help_usage_str()
        if command_help_str is not None:
            if command_help_str[-1] != '\n':
                command_help_str += '\n'
            help_txt += command_help_str

    print(help_txt)
