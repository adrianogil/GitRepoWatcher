
def execute(args, extra_args, controller):
    # if len(args) == 0:
    # category='%'
    # elif len(args) > 0:
    #     category = args[0]

    repo_list = controller.get_repos()

    index = 0
    for repo in repo_list:
        try:
            results = controller.push_commits_to_upstream(repo)

            if results['ok?']:
                print("###################################################")
                print('Repo ' + str(index) + ' - ' + repo.name + ': Sending ' + \
                    str(results['commits']) + ' commits\n')
                print(results['output'] + "\n")
        except:
            print("Caught error when handling repo " + str(repo.name))
        index = index + 1
    print("###################################################")
            


            