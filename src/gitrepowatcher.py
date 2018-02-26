#!/usr/bin/env python
import sys, sqlite3, os, subprocess

import utils

list_args = '--save -s'

# Open Connection
mydirs_directory = os.environ['GIT_REPO_WATCHER_DIR'] + '/db/'
conn = sqlite3.connect(mydirs_directory + 'repowatcher.sqlite');

# Creating cursor
c = conn.cursor()

# Create table
c.execute('''
    CREATE TABLE IF NOT EXISTS Repo (
        id_repo INTEGER,
        repo_name TEXT,
        repo_path TEXT,
        repo_category TEXT,
        update_command TEXT,
        PRIMARY KEY (id_repo)
    )
''')

def save_repo(args, extra_args):
    if len(args) == 0:
        update_command = 'git remote update'
        category = 'default'
    elif len(args) == 1:
        update_command = args[0]
        category = 'default'
    elif len(args) >= 2:
        update_command = args[0]
        category = args[1]

    repo_path = os.getcwd()
    repo_name = os.path.basename(repo_path)

    print('Saving repo ' + repo_name)
    print('Identified path ' + repo_path)
    print('Repo Category: ' + category)
    print('Using update-command as "' +  update_command + '"')

    c.execute("INSERT INTO Repo (repo_name,repo_path,repo_category,update_command) " + \
        "VALUES (:repo_name,:repo_path,:repo_category,:update_command)", \
        (repo_name, repo_path, category, update_command))
    conn.commit()

    print('Repo saved.')

def update_in_batch(args, extra_args):
    if len(args) == 0:
        category='%'
    elif len(args) > 0:
        category = args[0]

    c.execute("SELECT * from Repo WHERE repo_category LIKE ? ORDER BY id_repo",
        category)
    current_repo = ''
    index = 0;
    for row in c:
        try:
            index = index + 1
            print("###################################################")
            current_repo = str(row[1])
            print('Repo ' + str(index) + ': Updating ' + current_repo)
            update_command = 'cd "' + str(row[2]) + '" && ' + str(row[4])
            update_output = subprocess.check_output(update_command, shell=True)
            print(update_output)
        except:
            print("Caught error when updating repo " + str(current_repo))

def move_head_to_upstream(args, extra_args):
    category='%'

    c.execute("SELECT * from Repo WHERE repo_category LIKE ? ORDER BY id_repo",
        category)
    current_repo = ''
    index = 0;
    for row in c:
        try:
            index = index + 1
            print("###################################################")
            current_repo = str(row[1])
            print('Repo ' + str(index) + ': Move HEAD to upstream in ' + current_repo)
            get_upstream_name = ' git rev-parse --abbrev-ref --symbolic-full-name @{u}'
            get_upstream_command = 'cd "' + str(row[2]) + '" && ' + get_upstream_name
            upstream = subprocess.check_output(get_upstream_command, shell=True)

            get_unstaged_files = 'git diff --numstat | wc -l'
            get_unstaged_command = 'cd "' + str(row[2]) + '" && ' + get_unstaged_files
            unstaged = subprocess.check_output(get_unstaged_command, shell=True)
            unstaged = unstaged.strip()

            # print(unstaged)

            if unstaged == '0':
                get_diverge_commits = 'git log origin/master..HEAD --pretty=oneline | wc -l'
                get_diverge_commits_command = 'cd "' + str(row[2]) + '" && ' + get_diverge_commits
                diverge_commits = subprocess.check_output(get_diverge_commits_command, shell=True)
                diverge_commits = diverge_commits.strip()

                if diverge_commits == '0':
                    move_upstream = ' git reset --hard ' + upstream.strip()
                    move_upstream_command = 'cd "' + str(row[2]) + '" && ' + move_upstream
                    move_output = subprocess.check_output(move_upstream_command, shell=True)
                    print(move_output)
                else:
                    print('There are commits to be synced with upstream in repo!')
            else:
                print('There are unstaged changes in repo!')
        except:
            print("Caught error when handling repo " + str(current_repo))


def list_all_saved_repo(args, extra_args):
    c.execute("SELECT * from Repo ORDER BY id_repo")
    index = 0
    for row in c:
        print('Repo ' + str(index) + ': ' + str(row[1]))
        print('- path: ' + str(row[2]))
        print('- category: ' + str(row[3]))
        print('- update command: ' + str(row[4]))
        index = index + 1

commands_parse = {
    '-s'       : save_repo,
    '-u'       : update_in_batch,
    '-l'       : list_all_saved_repo,
    '-up'      : move_head_to_upstream,
    '--save'   : save_repo,
    '--update' : update_in_batch,
    '--list'   : list_all_saved_repo,
}

def parse_arguments():

    args = {}

    last_key = ''

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
    # print('DEBUG: Parsing args: ' + str(args))
    for a in args:
        if a in commands_parse:
            commands_parse[a](args[a], args)

args = parse_arguments()
parse_commands(args)
