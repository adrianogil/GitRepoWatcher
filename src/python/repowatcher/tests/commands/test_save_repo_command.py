from types import SimpleNamespace

from repowatcher.commands import save_repo_command


class _CategoryDao:
    def __init__(self):
        self.default_category = SimpleNamespace(name="default")

    def get(self, name):
        return SimpleNamespace(name=name)

    def save(self, name):
        return SimpleNamespace(name=name)


class _EntityFactory:
    def create_repo(self, args):
        return SimpleNamespace(**args)


class _Controller:
    def __init__(self, existing_repos):
        self.categoryDAO = _CategoryDao()
        self.entity_factory = _EntityFactory()
        self._existing_repos = existing_repos
        self.saved_repos = []

    def get_repos(self, conditions):
        assert "path" in conditions
        return self._existing_repos

    def save_repo(self, repo):
        self.saved_repos.append(repo)
        return SimpleNamespace(success=True, data=SimpleNamespace(id=42))


def test_execute_allows_same_repo_name_when_paths_differ(monkeypatch, capsys):
    monkeypatch.setattr(save_repo_command, "get_git_root", lambda _: "/repos/team/shared-name")
    monkeypatch.setattr(save_repo_command.os, "getcwd", lambda: "/repos/team/shared-name")

    controller = _Controller(existing_repos=[SimpleNamespace(id=10, path="/other/place/shared-name")])

    save_repo_command.execute([], {}, controller)

    output = capsys.readouterr().out
    assert "Repo saved with ID 42" in output
    assert len(controller.saved_repos) == 1
    assert controller.saved_repos[0].path == "/repos/team/shared-name"


def test_execute_rejects_same_repo_path(monkeypatch, capsys):
    monkeypatch.setattr(save_repo_command, "get_git_root", lambda _: "/repos/team/shared-name")
    monkeypatch.setattr(save_repo_command.os, "getcwd", lambda: "/repos/team/shared-name")

    controller = _Controller(existing_repos=[SimpleNamespace(id=10, path="/repos/team/shared-name")])

    save_repo_command.execute([], {}, controller)

    output = capsys.readouterr().out
    assert "Error: repo already saved with ID 10" in output
    assert len(controller.saved_repos) == 0
