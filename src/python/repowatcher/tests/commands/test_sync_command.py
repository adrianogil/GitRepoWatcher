from repowatcher.commands import sync_command


class _Repo:
    def __init__(self, name):
        self.name = name


class _Controller:
    def __init__(self, repos, rebase_ok_by_name):
        self._repos = repos
        self._rebase_ok_by_name = rebase_ok_by_name
        self.calls = []

    def get_search_conditions(self, args, extra_args):
        self.calls.append(("get_search_conditions", args, extra_args))
        return {"categories": args}

    def get_repos(self, search_conditions):
        self.calls.append(("get_repos", search_conditions))
        return self._repos

    def remote_update(self, repo):
        self.calls.append(("remote_update", repo.name))
        return f"remote update {repo.name}"

    def rebase(self, repo):
        self.calls.append(("rebase", repo.name))
        return {"ok?": self._rebase_ok_by_name[repo.name], "output": f"rebase {repo.name}"}

    def abort_rebase(self, repo):
        self.calls.append(("abort_rebase", repo.name))
        return f"abort rebase {repo.name}"

    def push(self, repo):
        self.calls.append(("push", repo.name))
        return f"push {repo.name}"


def test_execute_runs_full_sync_for_rebase_success():
    repo = _Repo("repo-ok")
    controller = _Controller([repo], {"repo-ok": True})

    sync_command.execute(["team"], {"--sync": ["team"]}, controller)

    assert ("remote_update", "repo-ok") in controller.calls
    assert ("rebase", "repo-ok") in controller.calls
    assert ("push", "repo-ok") in controller.calls
    assert ("abort_rebase", "repo-ok") not in controller.calls


def test_execute_aborts_rebase_and_skips_push_when_rebase_fails():
    repo = _Repo("repo-fail")
    controller = _Controller([repo], {"repo-fail": False})

    sync_command.execute([], {"--sync": []}, controller)

    assert ("remote_update", "repo-fail") in controller.calls
    assert ("rebase", "repo-fail") in controller.calls
    assert ("abort_rebase", "repo-fail") in controller.calls
    assert ("push", "repo-fail") not in controller.calls
