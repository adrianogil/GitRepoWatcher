from types import SimpleNamespace

import pytest

from repowatcher.commands import import_command


class _EntityFactory:
    def __init__(self):
        self.created_args = []

    def create_repo(self, args):
        self.created_args.append(args)
        return SimpleNamespace(**args)


class _Controller:
    def __init__(self, git_roots=None):
        self.entity_factory = _EntityFactory()
        self.git_roots = git_roots or {}
        self.git_root_requests = []
        self.category_requests = []
        self.saved_repos = []

    def get_git_root(self, path):
        self.git_root_requests.append(path)
        return self.git_roots.get(path)

    def get_category(self, name):
        self.category_requests.append(name)
        return SimpleNamespace(id=5, name=name)

    def save_repo(self, repo):
        self.saved_repos.append(repo)
        return SimpleNamespace(success=True, data=SimpleNamespace(id=42))


def _write_csv(tmp_path, contents):
    csv_path = tmp_path / "repos.csv"
    csv_path.write_text(contents, encoding="utf-8")
    return csv_path


@pytest.mark.parametrize(
    "row",
    [
        "/repos/project,git pull",
        "/repos/project,git pull,work,unexpected",
        '"/repos/project,git pull,work',
    ],
)
def test_import_rejects_malformed_row_without_calling_controller(tmp_path, capsys, row):
    csv_path = _write_csv(tmp_path, "Path,UpdateCommand,Category\n" + row + "\n")
    controller = _Controller()

    import_command.execute([str(csv_path)], {}, controller)

    assert "Error: malformed CSV row 2" in capsys.readouterr().out
    assert controller.git_root_requests == []
    assert controller.entity_factory.created_args == []
    assert controller.saved_repos == []


def test_import_rejects_missing_required_columns(tmp_path, capsys):
    csv_path = _write_csv(
        tmp_path,
        "Path,Category\n/repos/project,work\n",
    )
    controller = _Controller()

    import_command.execute([str(csv_path)], {}, controller)

    assert "Error: missing required CSV columns: UpdateCommand" in capsys.readouterr().out
    assert controller.git_root_requests == []
    assert controller.entity_factory.created_args == []
    assert controller.saved_repos == []


def test_import_rejects_non_git_repo_path(tmp_path, capsys):
    csv_path = _write_csv(
        tmp_path,
        "Path,UpdateCommand,Category\n/not/a/repo,git pull,work\n",
    )
    controller = _Controller()

    import_command.execute([str(csv_path)], {}, controller)

    output = capsys.readouterr().out
    assert "/not/a/repo" in output
    assert "Current path is not a git project" in output
    assert controller.git_root_requests == ["/not/a/repo"]
    assert controller.category_requests == []
    assert controller.entity_factory.created_args == []
    assert controller.saved_repos == []


def test_import_saves_valid_row_with_controller_entities(tmp_path, capsys):
    csv_path = _write_csv(
        tmp_path,
        "Path,UpdateCommand,Category\n/repos/project,git pull --rebase,work\n",
    )
    controller = _Controller({"/repos/project": "/resolved/project"})

    import_command.execute([str(csv_path)], {}, controller)

    output = capsys.readouterr().out
    assert "Repo saved with ID 42" in output
    assert controller.git_root_requests == ["/repos/project"]
    assert controller.category_requests == ["work"]
    assert controller.entity_factory.created_args == [
        {
            "name": "project",
            "path": "/resolved/project",
            "categories": [SimpleNamespace(id=5, name="work")],
            "update_command": "git pull --rebase",
        }
    ]
    assert len(controller.saved_repos) == 1
    assert controller.saved_repos[0].path == "/resolved/project"
