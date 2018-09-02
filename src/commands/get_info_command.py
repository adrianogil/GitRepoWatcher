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

    search_conditions = get_search_conditions(args, extra_args, controller)

    repo_list = controller.get_repos(search_conditions)

    index = 0
    for repo in repo_list:
        print('Repo ' + str(index) + ': ' + str(repo.name) + " (ID: " + str(repo.id) + ")")
        print('- path: ' + str(repo.path))
        print('- categories: ')
        for c in repo.categories:
            print('--\t' + c.name)
        print('- update command: ' + str(repo.update_command))
        index = index + 1

    if len(repo_list) == 0:
        print('Current path is not saved as a repo.')