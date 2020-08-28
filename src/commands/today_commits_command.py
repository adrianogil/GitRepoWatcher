import json
import os


def execute(args, extra_args, controller):
    search_conditions = controller.get_search_conditions(args, extra_args)
    repo_list = controller.get_repos(search_conditions)

    total_commits_in_all_repos = 0
    index = 0

    report_data = {}

    for repo in repo_list:
        try:
            if not os.path.exists(repo.path):
                continue

            today_commits_msgs = controller.get_today_commits(repo)
            total_today_commits = len(today_commits_msgs)
            index = index + 1

            if total_today_commits > 0:
                report_data[repo.name] = {}
                report_data[repo.name]['repo-id'] = repo.id
                report_data[repo.name]['repo-path'] = repo.path
                total_commits_in_all_repos = total_commits_in_all_repos + total_today_commits
                commits = []
                for c in today_commits_msgs:
                    commit_data = {}

                    commit_data['commit-id'] = c.split(' ')[0]
                    commit_data['commit-msg'] = c[len(c.split(' ')[0]):].strip()

                    commits.append(commit_data)
                report_data[repo.name]['commits'] = commits
        except Exception as error:
            print(error)

    if '--json' in extra_args:
        # json_data = ['report', report_data]
        # parsed_json = json.loads(str(json_data))
        # print(json.dumps(parsed_json, indent=4, sort_keys=True))
        with open(extra_args['--json'][0], 'w') as f:
            json.dump(report_data, f)
    else:
        for r in report_data:
            print("###################################################")
            print('Repo %s (Id %s) ' % (r, report_data[r]['repo-id']))
            total_commits_in_all_repos = total_commits_in_all_repos + total_today_commits
            for c in report_data[r]['commits']:
                print(c['commit-id'] + " " + c['commit-msg'])
        print("###################################################")
        print('Today, there were generated %s commits in %s repos.' % (total_commits_in_all_repos, index))
