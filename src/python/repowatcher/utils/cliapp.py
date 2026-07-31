from .flags import process_args


RESERVED_OPTION_FLAGS = frozenset({
    "-c",
    "-cs",
    "-nc",
    "-rc",
    "--all",
    "--debug",
    "--json",
    "--obsidian",
    "--path",
})


class CliController:
    """
    This class represents a controller for the CLI application.
    """

    def get_commands(self):
        """
        Returns a list of available commands.
        """
        commands = [

        ]

        return commands


class CliApp:
    """
    Represents a command-line application.

    Args:
        controller (CliController): The controller object for the application.

    Attributes:
        controller (CliController): The controller object for the application.
    """

    def __init__(self, controller: CliController):
        self.controller = controller

    def run(self):
        """
        Runs the command-line application.

        This method processes the command-line arguments and calls the appropriate command handler.
        """
        args = process_args()
        self._parse_commands(args)

    def _parse_commands(self, args):
        """
        Parses the command-line arguments and calls the appropriate command handler.

        Args:
            args (dict): A dictionary containing the command-line arguments.

        Returns:
            None
        """
        if args is None:
            return

        commands_parse = self.controller.get_commands()

        if not args:
            if 'no-args' in commands_parse:
                commands_parse['no-args']()
            else:
                print('Command not found')
            return

        command_flags = [arg for arg in args if arg in commands_parse]

        if not command_flags:
            print('Command not found')
            return

        if len(command_flags) > 1:
            print('Only one command can be specified: ' + ', '.join(command_flags))
            return

        command_flag = command_flags[0]
        commands_parse[command_flag](args[command_flag], args, self.controller)
