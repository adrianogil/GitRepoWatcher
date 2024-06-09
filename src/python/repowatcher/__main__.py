from repowatcher.gitrepocontroller import GitRepoController

import repowatcher.utils as utils

from pyutils.cli.cliapp import CliApp

import sys
import os

if '--debug' in sys.argv:
    utils.printlog.debug_mode = True

repo_watcher_environ_var = 'GIT_REPO_WATCHER_DIR'
if repo_watcher_environ_var in os.environ:
    db_directory = os.environ[repo_watcher_environ_var] + '/../db/'
else:
    db_directory = "../../db/"

print("Using database directory: " + db_directory)
controller = GitRepoController(db_directory)
app = CliApp(controller)
app.run()
