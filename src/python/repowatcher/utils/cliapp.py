from .flags import process_args

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

        command_found = False
        for a in args:
            if a in commands_parse:
                command_found = True
                if commands_parse[a](args[a], args, self.controller):
                    break
        if not command_found:
            print('Command not found')
