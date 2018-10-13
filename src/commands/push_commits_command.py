
def execute(args, extra_args, controller):
    # if len(args) == 0:
    # category='%'
    # elif len(args) > 0:
    #     category = args[0]

    repo_list = controller.get_repos()

    index = 0
    for repo in repo_list:
        # print('Repo ' + str(index) + ': ' + str(repo.name) + " (ID: " + str(repo.id) + ")")
        # print('- path: ' + str(repo.path))
        # print('- categories: ')
        # for c in repo.categories:
        #     print('--\t' + c.name)
        # print('- update command: ' + str(repo.update_command))

        current_repo = str(row[1])
        path = row[2]
        results = controller.push_commits_to_upstream(repo)

        if results['ok?']:
            print("###################################################")
            print('Repo ' + str(index) + ' - ' + repo.name + ': Sending ' + \
                str(results['commits']) + ' commits\n')
            print(results['output'] + "\n")
        except:
            print("Caught error when handling repo " + str(current_repo))
        index = index + 1
    print("###################################################")
            


            