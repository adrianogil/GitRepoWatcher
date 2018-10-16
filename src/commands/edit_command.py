import os

def execute(args, extra_args, controller):

    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    new_categories_to_add = []
    if '-nc' in extra_args:
        for c in extra_args['-nc']:
            new_cat_obj = controller.get_category(c)
            if not new_cat_obj in new_categories_to_add:
                new_categories_to_add.append(new_cat_obj)

    categories_to_remove = []
    if '-rc' in extra_args:
        for c in extra_args['-rc']:
            cat_obj = controller.get_category(c)
            if not cat_obj in categories_to_remove:
                categories_to_remove.append(cat_obj)

    index = 0
    for repo in repo_list:
        print('Editing repo info ' + str(index) + ': ' + str(repo.name) + " (ID: " + str(repo.id) + ")")
        print('- categories: ')
        new_cats = []
        for n in new_categories_to_add:
            for c in repo.categories:
                if n.id == c.id:
                    break
            else:
                new_cats.append(n)

        for n in new_cats:
            print('\t-- Added ' + n.name)
            repo.categories.append(n)

        if categories_to_remove is not None and len(categories_to_remove) > 0:
            new_cats = []
            for c in repo.categories:
                for rc in categories_to_remove:
                    if c.name == rc.name:
                        break
                else:
                    new_cats.append(c)
            repo.categories = new_cats

        # for c in repo.categories:
        #     print('DEBUG current cat: ' + c.name)

        controller.update_edit(repo)
        
        index = index + 1

    if len(repo_list) == 0:
        print('No repo was found!')