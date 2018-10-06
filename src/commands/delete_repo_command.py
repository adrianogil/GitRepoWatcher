import os

def get_search_conditions(args, extra_args, controller):

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

def execute(args, extra_args, controller):
    repo_list = controller.get_repos()

    # if len(args) == 0:
    #     repo_path = os.getcwd()
    #     sql_query_delete = "DELETE FROM Repo WHERE repo_path = ?"
    #     delete_data = (repo_path,)
    # elif len(args) == 1:
    #     id_repo = int(args[0])
    #     sql_query_delete = "DELETE FROM Repo WHERE id_repo = ?"
    #     delete_data = (id_repo,)
    
    search_conditions = get_search_conditions(args, extra_args, controller)

    repo_list = controller.get_repos(search_conditions)

    controller.delete_repos(repo_list)