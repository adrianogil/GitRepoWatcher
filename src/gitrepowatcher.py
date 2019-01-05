
import sys, os, subprocess

import utils

import codecs
import locale

from gitrepocontroller import GitRepoController

# Wrap sys.stdout into a StreamWriter to allow writing unicode.
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

db_directory = os.environ['GIT_REPO_WATCHER_DIR'] + '/../db/'

controller = GitRepoController(db_directory)

commands_parse = controller.get_commands()

def parse_arguments():

    args = {}

    last_key = ''

    if len(sys.argv) == 1:
        controller.handle_no_args()
        return None

    for i in xrange(1, len(sys.argv)):
        a = sys.argv[i]
        if a[0] == '-' and not utils.is_float(a):
            last_key = a
            args[a] = []
        elif last_key != '':
            arg_values = args[last_key]
            arg_values.append(a)
            args[last_key] = arg_values

    return args

def parse_commands(args):
    if args is None:
        return

    # print('DEBUG: Parsing args: ' + str(args))
    for a in args:
        if a in commands_parse:
            commands_parse[a](args[a], args, controller)

args = parse_arguments()
parse_commands(args)