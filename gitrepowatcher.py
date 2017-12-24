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
        update_command TEXT,
        PRIMARY KEY (id_repo)
    )
''')

def save_repo(update_command='git remote update'):
    repo_path = os.getcwd()
    repo_name = os.path.basename(repo_path)

    print('Saving repo ' + repo_name)
    print('Identified path ' + repo_path)
    print('Using update-command as "' +  update_command + '"')

    dict_path = {":path" : os.getcwd(), ":key": sys.argv[2]}
    #print dict_path
    c.execute("INSERT INTO Repo (repo_name,repo_path,update_command) VALUES (:repo_name,:repo_path,:update_command)", \
        (repo_name, repo_path, update_command))
    conn.commit()
    
    print('Repo saved.')

def update_in_batch():
    c.execute("SELECT * from Repo ORDER BY id_repo")
    for row in c:
        print('Update repo ' + str(row[1]))
        update_command = 'cd "' + str(row[2]) + '" && ' + str(row[3])
        update_output = subprocess.check_output(update_command, shell=True)
        print(update_output)

if len(sys.argv) == 3:
    if sys.argv[1] == '--save' or sys.argv[1] == '-s':
        save_repo(sys.argv[2])
elif len(sys.argv) == 2:
    if sys.argv[1] == '--save' or sys.argv[1] == '-s':
        save_repo()
    elif sys.argv[1] == '--batch' or sys.argv[1] == '-b':
        update_in_batch()
