import sqlite3, os

import gitcommands
import utils, importutils

importutils.addpath(__file__, 'dao')
from dao.repodao import RepoDAO
from dao.categorydao import CategoryDAO

importutils.addpath(__file__, 'entity')
from entity.entityfactory import EntityFactory

importutils.addpath(__file__, 'commands')
import commands.save_repo_command

class OperationObject:
    def __init__(self, operation_success, data):
        self.success = operation_success
        self.data = data

class GitRepoController:
    def __init__(self, db_directory):
        # Open Connection
        conn = sqlite3.connect(db_directory + 'repowatcher2.sqlite');

        # Creating cursor
        c = conn.cursor()

        self.entity_factory = EntityFactory()
        self.categoryDAO = CategoryDAO(conn, c, self.entity_factory)
        self.repoDAO = RepoDAO(conn, c, self.entity_factory, self.categoryDAO)

        self.categoryDAO.create_tables()
        self.repoDAO.create_tables()

    def get_commands(self):
        commands_parse = {
            # '-i'           : get_info,
            # '-c'           : verify_changes,
            '-s'           : commands.save_repo_command.execute,
            # '-u'           : update_in_batch,
            # '-l'           : list_all_saved_repo,
            # '-d'           : delete_saved_repo,
            # '-up'          : move_head_to_upstream,
            # '-pc'          : push_commits,
            # '--exec'       : execute_batch_command,
            # '--save'       : save_repo,
            # '--list'       : list_all_saved_repo,
            # '--stats'      : get_commit_stats,
            # '--today'      : get_commits_of_today,
            # '--update'     : update_in_batch,
            # '--delete-all' : delete_all_repos,
            # 'no-args'      : handle_no_args,
        }
        return commands_parse

    def save_repo(self, repo):

        saved_repo = self.repoDAO.save(repo)
        return OperationObject(saved_repo is not None, saved_repo)