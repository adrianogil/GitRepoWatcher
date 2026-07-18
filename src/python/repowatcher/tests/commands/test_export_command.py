import csv

from repowatcher.commands import export_command


class _Category:
    def __init__(self, name):
        self.name = name


class _Repo:
    def __init__(self, repo_id, path, update_command, categories=None):
        self.id = repo_id
        self.path = path
        self.update_command = update_command
        self.categories = categories or []


class _Controller:
    def __init__(self, repos):
        self.repos = repos

    def get_repos(self):
        return self.repos


def test_export_writes_utf8_csv_rows_to_filename_with_spaces(tmp_path):
    output_path = tmp_path / "repo export.csv"
    controller = _Controller(
        [
            _Repo(
                1,
                "/tmp/repo with spaces",
                "git pull --rebase",
                [_Category("pesquisa")],
            ),
            _Repo(
                2,
                "/tmp/repositório",
                "git remote update",
                [_Category("ação")],
            ),
        ]
    )

    export_command.execute([str(output_path)], {}, controller)

    with open(output_path, newline="", encoding="utf-8") as csvfile:
        rows = list(csv.reader(csvfile))

    assert rows == [
        ["RepoId", "Path", "UpdateCommand", "Category"],
        ["1", "/tmp/repo with spaces", "git pull --rebase", "pesquisa"],
        ["2", "/tmp/repositório", "git remote update", "ação"],
    ]


def test_export_writes_empty_category_when_repo_has_no_categories(tmp_path):
    output_path = tmp_path / "repos.csv"
    controller = _Controller(
        [
            _Repo(1, "/tmp/repo", "git pull", []),
        ]
    )

    export_command.execute([str(output_path)], {}, controller)

    with open(output_path, newline="", encoding="utf-8") as csvfile:
        rows = list(csv.reader(csvfile))

    assert rows == [
        ["RepoId", "Path", "UpdateCommand", "Category"],
        ["1", "/tmp/repo", "git pull", ""],
    ]
