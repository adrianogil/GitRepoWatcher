from types import SimpleNamespace

from repowatcher.commands import delete_repo_command


class _Controller:
    def __init__(self, search_conditions, repos=None):
        self.search_conditions = search_conditions
        self.repos = repos or []
        self.calls = []

    def get_search_conditions(self, args, extra_args):
        self.calls.append(("get_search_conditions", args, extra_args))
        return self.search_conditions

    def get_repos(self, search_conditions):
        self.calls.append(("get_repos", search_conditions))
        return self.repos

    def delete_repos(self, repos):
        self.calls.append(("delete_repos", repos))


def test_execute_refuses_unfiltered_delete_without_explicit_all(capsys):
    controller = _Controller(search_conditions={})

    delete_repo_command.execute([], {"-d": []}, controller)

    assert controller.calls == [
        ("get_search_conditions", [], {"-d": []}),
    ]
    assert "Refusing to delete repositories without a selector" in capsys.readouterr().out


def test_execute_deletes_repos_matching_selector():
    repo = SimpleNamespace(id=7, name="selected")
    controller = _Controller(search_conditions={"id": 7}, repos=[repo])

    delete_repo_command.execute(["7"], {"-d": ["7"]}, controller)

    assert controller.calls == [
        ("get_search_conditions", ["7"], {"-d": ["7"]}),
        ("get_repos", {"id": 7}),
        ("delete_repos", [repo]),
    ]


def test_execute_allows_unfiltered_delete_with_explicit_all():
    repos = [
        SimpleNamespace(id=1, name="first"),
        SimpleNamespace(id=2, name="second"),
    ]
    extra_args = {"-d": [], "--all": []}
    controller = _Controller(search_conditions={}, repos=repos)

    delete_repo_command.execute([], extra_args, controller)

    assert controller.calls == [
        ("get_search_conditions", [], extra_args),
        ("get_repos", {}),
        ("delete_repos", repos),
    ]
