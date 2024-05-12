import sys
import os

import utils

from .gitrepocontroller import GitRepoController

from pyutils.cli.cliapp import CliApp


db_directory = os.environ['GIT_REPO_WATCHER_DIR'] + '/../db/'
controller = GitRepoController(db_directory)

app = CliApp(controller)
app.run()
