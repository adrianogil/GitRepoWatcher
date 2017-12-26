#!/usr/bin/env python
import sys, sqlite3, os, subprocess

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

def save_repo(update_command='git remote update', category='default'):
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

def update_in_batch(category='%'):
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


def list_all_saved_repo():
    c.execute("SELECT * from Repo ORDER BY id_repo")
    index = 0
    for row in c:
        print('Repo ' + str(index) + ': ' + str(row[1]))
        print('- path: ' + str(row[2]))
        print('- category: ' + str(row[3]))
        print('- update command: ' + str(row[4]))
        index = index + 1

if len(sys.argv) == 4:
    if sys.argv[1] == '--save' or sys.argv[1] == '-s':
        save_repo(sys.argv[3],sys.argv[2])
elif len(sys.argv) == 3:
    if sys.argv[1] == '--save' or sys.argv[1] == '-s':
        save_repo(sys.argv[2])
elif len(sys.argv) == 2:
    if sys.argv[1] == '--save' or sys.argv[1] == '-s':
        save_repo()
    elif sys.argv[1] == '--batch' or sys.argv[1] == '-b':
        update_in_batch()
    elif sys.argv[1] == '--list' or sys.argv[1] == '-l':
        list_all_saved_repo()
