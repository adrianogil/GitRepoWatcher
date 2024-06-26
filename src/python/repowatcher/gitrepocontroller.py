from repowatcher.dao.repodao import RepoDAO
from repowatcher.dao.categorydao import CategoryDAO
from repowatcher.entity.entityfactory import EntityFactory

import repowatcher.gitcommands as gitcommands
import repowatcher.utils as utils

import repowatcher.commands.list_repos_command as list_repos_command
from repowatcher.commands.available_commands import get_available_commands

from pyutils.cli.cliapp import CliController

import subprocess
import sqlite3
import os



class OperationObject:
    def __init__(self, operation_success, data):
        self.success = operation_success
        self.data = data

class GitRepoController(CliController):
    def __init__(self, db_directory):

        self.available_commands = []

        if not os.path.exists(db_directory):
            os.makedirs(db_directory)

        # Open Connection
        conn = sqlite3.connect(db_directory + 'gitrepowatcher.sqlite');

        # Creating cursor
        c = conn.cursor()

        self.entity_factory = EntityFactory()
        self.categoryDAO = CategoryDAO(conn, c, self.entity_factory)
        self.repoDAO = RepoDAO(conn, c, self.entity_factory, self.categoryDAO)

        self.categoryDAO.create_tables()
        self.repoDAO.create_tables()

    def handle_no_args(self):
        print("Default mode: Update and Move HEAD to upstream\n")
        # update_batch_command.execute([], [], self)
        # move_head_command.execute([], [], self)
        list_repos_command.execute([], [], self)

    def define_commands(self):
        self.available_commands = get_available_commands()

    def get_commands(self):
        commands_parse = {
            'no-args'      : self.handle_no_args,
        }
        self.define_commands()

        for cmd in self.available_commands:
            cmd_flags = cmd.get_cmd_flags()
            for flag in cmd_flags:
                commands_parse[flag] = cmd.execute

        return commands_parse

    def get_git_root(self, path):
        return gitcommands.get_git_root(path)

    def update_gitrepo(self, repo):
        diverge_commits = ""

        update_command = 'cd "' + repo.path + '" && ' + repo.update_command

        def preexec_function():
            os.setpgrp()

        try:
            update_output = subprocess.check_output(update_command, shell=True, stdin=subprocess.PIPE, preexec_fn=preexec_function)
            update_output = update_output.decode("utf-8").strip()
            print(update_output)

            diverge_commits = gitcommands.get_diverge_commits_HEAD_to_upstream(repo.path)
            print(diverge_commits + ' new commits')
        except:
            print("error while updating %s" % (repo.name,))

        return diverge_commits

    def save_repo(self, repo):
        saved_repo = self.repoDAO.save(repo)
        return OperationObject(saved_repo is not None, saved_repo)

    def update_edit(self, repo):
        saved_repo = self.repoDAO.update(repo)

    def get_repos(self, conditions):
        return self.repoDAO.get_all(conditions)

    def get_categories(self, conditions={}):
        return self.categoryDAO.get_all()

    def get_unstaged_files(self, repo):
        current_repo = repo.name
        print('Repo ' + str(repo.id) + ': Verify changes in ' + current_repo)
        unstaged = gitcommands.get_unstaged_files(repo.path)

        return unstaged

    def get_total_commits(self, repo):
        total_commits = gitcommands.get_diverge_commits_upstream_to_HEAD(repo.path)
        return total_commits

    def delete_repos(self, repos):
        for r in repos:
            self.repoDAO.delete(r)

    # Return category object
    def get_category(self, category_name):
        if category_name.lower() == self.categoryDAO.default_category.name.lower():
            return self.categoryDAO.default_category

        cat_obj = self.categoryDAO.get(category_name)
        if cat_obj is None:
            cat_obj = self.categoryDAO.save(category_name)
        return cat_obj

    def get_search_conditions(self, args, extra_args):

        search_conditions = {}

        if '--all' in extra_args:
            return {}

        def add_category(cat):

            if 'categories' in search_conditions:
                cat_list = search_conditions['categories']
                cat_list.append(cat)
                search_conditions['categories'] = cat_list
            else:
                search_conditions['categories'] = [cat]

        for a in args:
            if utils.is_int(a):
                search_conditions['id'] = int(a)
            elif os.path.isdir(a):
                search_conditions['path'] = a
            elif len(a) > 5 and a[:2] == 'git':
                search_conditions['update_command'] = a
            else:
                add_category(a)

        if '-cs' in extra_args:
            for c in extra_args['-cs']:
                add_category(c)

        if "--path" in extra_args:
            search_conditions['path'] = extra_args["--path"]
        if "-p" in extra_args:
            search_conditions['path'] = extra_args["-p"]

        # if not 'path' in search_conditions:
        #     search_conditions['path'] = gitcommands.get_git_root(os.getcwd())

        # print('DEBUG: search_conditions - ' + str(search_conditions))

        return search_conditions

    def get_diverge_commits_to_upstream(self, repo):
        diverge_commits = gitcommands.get_diverge_commits_HEAD_to_upstream(repo.path)

        return diverge_commits

    def get_diverge_commits_from_upstream(self, repo):
        diverge_commits = gitcommands.get_diverge_commits_upstream_to_HEAD(repo.path)

        return diverge_commits

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

    def get_total_commits(self, repo):

        return gitcommands.get_total_commits(repo.path)

    def get_today_commits(self, repo):

        return gitcommands.get_today_commits(repo.path)

    def get_last_commit(self, repo):

        return gitcommands.get_last_commit(repo.path)

    def get_last_commit_date(self, repo):

        return gitcommands.get_last_commit_date(repo.path)
