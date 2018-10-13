import sqlite3, os

import subprocess

import gitcommands
import utils, importutils

importutils.addpath(__file__, 'dao')
from dao.repodao import RepoDAO
from dao.categorydao import CategoryDAO

importutils.addpath(__file__, 'entity')
from entity.entityfactory import EntityFactory

importutils.addpath(__file__, 'commands')
import commands.verify_change_command
import commands.delete_repo_command
import commands.update_batch_command
import commands.list_repos_command
import commands.save_repo_command
import commands.move_head_command
import commands.get_info_command


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
            '-c'           : commands.verify_change_command.execute,
            '-l'           : commands.list_repos_command.execute,
            '-s'           : commands.save_repo_command.execute,
            '-i'           : commands.get_info_command.execute,
            '-u'           : commands.update_batch_command.execute,
            '-d'           : commands.delete_repo_command.execute,
            '-up'          : commands.move_head_command.execute,
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

    def update_gitrepo(self, repo):
        update_command = 'cd "' + repo.path + '" && ' + repo.update_command

        def preexec_function():
            os.setpgrp()

        update_output = subprocess.check_output(update_command, shell=True, stdin=subprocess.PIPE, preexec_fn=preexec_function)
        print(update_output)

        diverge_commits = gitcommands.get_diverge_commits_HEAD_to_upstream(repo.path)
        print(diverge_commits + ' new commits')


    def save_repo(self, repo):

        saved_repo = self.repoDAO.save(repo)
        return OperationObject(saved_repo is not None, saved_repo)

    def get_repos(self, conditions=[]):
        return self.repoDAO.get_all(conditions)

    def get_unstaged_files(self, repo):
        current_repo = repo.name
        print('Repo ' + str(repo.id) + ': Verify changes in ' + current_repo)
        get_upstream_name = ' git rev-parse --abbrev-ref --symbolic-full-name @{u}'
        get_upstream_command = 'cd "' + repo.path + '" && ' + get_upstream_name
        upstream = subprocess.check_output(get_upstream_command, shell=True)
        upstream = upstream.strip()

        get_unstaged_files = 'git diff --numstat | wc -l'
        get_unstaged_command = 'cd "' + repo.path + '" && ' + get_unstaged_files
        unstaged = subprocess.check_output(get_unstaged_command, shell=True)
        unstaged = unstaged.strip()

        return unstaged

    def get_total_commits(self, repo):
        total_commits = gitcommands.get_diverge_commits_upstream_to_HEAD(repo.path)
        return total_commits

    def delete_repos(self, repos):
        for r in repos:
            self.repoDAO.delete(r)

    def get_search_conditions(self, args, extra_args):

        search_conditions = {}

        for a in args:
            if utils.is_int(a):
                search_conditions['id'] = int(a)
            elif os.path.isdir(a):
                search_conditions['path'] = a
            elif len(a) > 5 and a[:2] == 'git':
                search_conditions['update_command'] = a
            else:
                if 'categories' in search_conditions:
                    cat_list = search_conditions['categories']
                    cat_list.append(a)
                    search_conditions['categories'] = cat_list
                else:
                    search_conditions['categories'] = [a]

        if not 'path' in search_conditions:
            search_conditions['path'] = os.getcwd()        

        return search_conditions

    def get_diverge_commits_to_upstream(self, repo):
        diverge_commits = gitcommands.get_diverge_commits_HEAD_to_upstream(repo.path)

        return diverge_commits

    def get_diverge_commits_from_upstream(self, repo):
        diverge_commits = gitcommands.get_diverge_commits_upstream_to_HEAD(repo.path)

        return diverge_commits


    def get_unstaged_files(self, repo):
        get_unstaged_files = 'git diff --numstat | wc -l'
        get_unstaged_command = 'cd "' + repo.path + '" && ' + get_unstaged_files
        unstaged = subprocess.check_output(get_unstaged_command, shell=True)
        unstaged = unstaged.strip()

        return unstaged

    def move_to_upstream(self, repo):
        upstream = gitcommands.get_upstream_name(repo.path)

        move_upstream = ' git reset --hard ' + upstream.strip()
        move_upstream_command = 'cd "' + repo.path + '" && ' + move_upstream
        move_output = subprocess.check_output(move_upstream_command, shell=True)

        return move_output

    def push_commits_to_upstream(self, repo):
        total_commits = gitcommands.get_diverge_commits_upstream_to_HEAD(repo.path)

        if total_commits > '0':
            command_output = gitcommands.push_commits_to_upstream(repo.path)
            return {"ok?": True, "commits" : total_commits,  "output" : command_output}
        return {"ok?": False}