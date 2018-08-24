import os

def get_search_conditions(args, extra_args, controller):

    search_conditions = {}

    for a in args:
        if utils.is_int(a):
            search_conditions['id'] = int(a)
        elif os.path.isdir(a):
            search_conditions['path'] = a
        elif len(a) > 5 and a[0:2] == 'git'
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


def execute(args, extra_args, controller):

    search_conditions = get_search_conditions(args, extra_args, controller)

    sql_query = "SELECT * from Repo WHERE " + query_conditions + " ORDER BY id_repo"
    # print('Debug: ' + sql_query)

    c.execute(sql_query,
        query_data)
    index = 0

    results = c.fetchall()

    for row in results:
        print('Repo ' + str(index) + ': ' + str(row[1]) + " (ID: " + str(row[0]) + ")")
        print('- path: ' + str(row[2]))
        print('- category: ' + str(row[3]))
        print('- update command: ' + str(row[4]))
        index = index + 1

    if len(args) == 0 and len(results) == 0:
        print('Current path is not saved as a repo.')