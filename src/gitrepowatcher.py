
import sys, sqlite3, os, subprocess

import utils

import gitcommands

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
        category = args[0]
        update_command = 'git remote update'
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

    c.execute("SELECT * from Repo WHERE repo_category LIKE ? ORDER BY id_repo",\
        (category,))
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

            diverge_commits = gitcommands.get_diverge_commits_HEAD_to_upstream(row[2])

            print(diverge_commits + ' new commits')
        except:
            print("Caught error when updating repo " + str(current_repo))

def move_head_to_upstream(args, extra_args):
    if len(args) == 0:
        category='%'
    elif len(args) > 0:
        category = args[0]

    c.execute("SELECT * from Repo WHERE repo_category LIKE ? ORDER BY id_repo",
        (category,))
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
            upstream = upstream.strip()

            get_unstaged_files = 'git diff --numstat | wc -l'
            get_unstaged_command = 'cd "' + str(row[2]) + '" && ' + get_unstaged_files
            unstaged = subprocess.check_output(get_unstaged_command, shell=True)
            unstaged = unstaged.strip()

            # print(unstaged)

            diverge_commits = gitcommands.get_diverge_commits_HEAD_to_upstream(row[2])
            if diverge_commits == '0':
                print('There are no new commits!')
            elif unstaged == '0':
                diverge_commits = gitcommands.get_diverge_commits_upstream_to_HEAD(row[2])

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
    if len(args) == 0:
        category='%'
    elif len(args) > 0:
        category = args[0]

    c.execute("SELECT * from Repo WHERE repo_category LIKE ? ORDER BY id_repo",
        (category,))
    index = 0
    for row in c:
        print('Repo ' + str(index) + ': ' + str(row[1]))
        print('- path: ' + str(row[2]))
        print('- category: ' + str(row[3]))
        print('- update command: ' + str(row[4]))
        index = index + 1

def delete_saved_repo(args, extra_args):
    if len(args) == 0:
        repo_path = os.getcwd()
        sql_query_delete = "DELETE FROM Repo WHERE repo_path = ?"
        delete_data = (repo_path,)
    elif len(args) == 1:
        id_repo = int(args[0])
        sql_query_delete = "DELETE FROM Repo WHERE id_repo = ?"
        delete_data = (id_repo,)
    c.execute(sql_query_delete, delete_data)
    conn.commit()

def delete_all_repos(args, extra_args):
    sql_query_delete = "DELETE FROM Repo"
    c.execute(sql_query_delete)
    conn.commit()

def verify_changes(args, extra_args):
    if len(args) == 0:
        category='%'
    elif len(args) > 0:
        category = args[0]

    c.execute("SELECT * from Repo WHERE repo_category LIKE ? ORDER BY id_repo",
        (category,))
    
    current_repo = ''
    index = 0;
    results = c.fetchall()

    unstaged_repos = []
    
    for row in results:
        try:
            index = index + 1
            print("###################################################")
            current_repo = str(row[1])
            print('Repo ' + str(index) + ': Verify changes in ' + current_repo)
            get_upstream_name = ' git rev-parse --abbrev-ref --symbolic-full-name @{u}'
            get_upstream_command = 'cd "' + str(row[2]) + '" && ' + get_upstream_name
            upstream = subprocess.check_output(get_upstream_command, shell=True)
            upstream = upstream.strip()

            get_unstaged_files = 'git diff --numstat | wc -l'
            get_unstaged_command = 'cd "' + str(row[2]) + '" && ' + get_unstaged_files
            unstaged = subprocess.check_output(get_unstaged_command, shell=True)
            unstaged = unstaged.strip()
            if unstaged != '0':
                print('There are unstaged changes in repo!')
                unstaged_repos.append({'id' : row[0], 'repo' : current_repo})
        except:
            print("Caught error when handling repo " + str(current_repo))
    print("###################################################")
    
    total_unstaged = len(unstaged_repos)
    if total_unstaged == 1:
        print("Found changes in only 1 repo:")
    else:
        print("Found changes in %s repos:" % (total_unstaged,))
    for u in unstaged_repos:
        print("  - (ID: %s) %s" % (u['id'], u['repo']))
    print("###################################################")


def get_info(args, extra_args):

    query_conditions = ''
    query_data = ()

    query_index = 0

    def add_condition(query_conditions, condition):
        if query_conditions == '':
            return condition
        else:
            return query_conditions + ' OR ' + condition

    if len(args) == 0:
        query_conditions = ' repo_path LIKE ? '
        query_data = (os.getcwd() + '%',)
    elif len(args) > 0:
        for a in args:
            if utils.is_int(args[0]):
                conditions = ' id_repo LIKE ? '
            else:
                conditions = ' repo_category LIKE ? '
            query_conditions = add_condition(query_conditions, conditions)
            query_data = query_data + (a,)
            query_index = query_index + 1

    
    sql_query = "SELECT * from Repo WHERE " + query_conditions + " ORDER BY id_repo"
    # print('Debug: ' + sql_query)

    c.execute(sql_query,
        query_data)
    index = 0

    results = c.fetchall()

    for row in results:
        print('Repo ' + str(index) + ': ' + str(row[1]))
        print('- path: ' + str(row[2]))
        print('- category: ' + str(row[3]))
        print('- update command: ' + str(row[4]))
        index = index + 1

    if len(args) == 0 and len(results) == 0:
        print('Current path is not saved as a repo.')

def get_commit_stats(args, extra_args):

    results = get_repos_from_args(args, extra_args)

    total_commits_in_all_repos = 0

    for row in results:
        print('Repo %s (Id %s) ' % (row[1],row[0]))
        total_commits = int(gitcommands.get_total_commits(row[2]))
        print('  Total commits: ' + str(total_commits))
        total_commits_in_all_repos = total_commits_in_all_repos + total_commits

    print('Commits in all repos: ' + str(total_commits_in_all_repos))

def get_repos_from_args(args, extra_args):
    query_conditions = ''
    query_data = ()

    query_index = 0

    def add_condition(query_conditions, condition):
        if query_conditions == '':
            return condition
        else:
            return query_conditions + ' OR ' + condition

    if len(args) == 0:
        query_conditions = ' repo_category LIKE ? '
        query_data = ('%',)
    elif len(args) > 0:
        for a in args:
            if utils.is_int(args[0]):
                conditions = ' id_repo LIKE ? '
            else:
                conditions = ' repo_category LIKE ? '
            query_conditions = add_condition(query_conditions, conditions)
            query_data = query_data + (a,)
            query_index = query_index + 1

    
    sql_query = "SELECT * from Repo WHERE " + query_conditions + " ORDER BY id_repo"
    # print('Debug: ' + sql_query)

    c.execute(sql_query,
        query_data)

    results = c.fetchall()

    return results

def get_commits_of_today(args, extra_args):
    results = get_repos_from_args(args, extra_args)

    total_commits_in_all_repos = 0

    for row in results:
        today_commits_msgs = gitcommands.get_today_commits(row[2])
        total_today_commits = len(today_commits_msgs)
        if total_today_commits > 0:
            print("###################################################")
            print('Repo %s (Id %s) ' % (row[1],row[0]))    
            total_commits_in_all_repos = total_commits_in_all_repos + total_today_commits
            for c in today_commits_msgs:
                print(c)

    print("###################################################")
    if len(args) == 0:
        print('Today, there were generated %s commits in all repos.' % (total_commits_in_all_repos,))
    else:
        print('Today, there were generated %s commits in repos.' % (total_commits_in_all_repos,))

commands_parse = {
    '-i'           : get_info,
    '-c'           : verify_changes,
    '-s'           : save_repo,
    '-u'           : update_in_batch,
    '-l'           : list_all_saved_repo,
    '-d'           : delete_saved_repo,
    '-up'          : move_head_to_upstream,
    '--save'       : save_repo,
    '--list'       : list_all_saved_repo,
    '--stats'      : get_commit_stats,
    '--today'      : get_commits_of_today,
    '--update'     : update_in_batch,
    '--delete-all' : delete_all_repos,
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
