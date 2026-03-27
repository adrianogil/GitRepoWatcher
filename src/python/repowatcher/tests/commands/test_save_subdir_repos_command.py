from repowatcher.commands import save_subdir_repos_command


class _Category:
    def __init__(self, name):
        self.name = name


class _CategoryDAO:
    def __init__(self):
        self.default_category = _Category("default")
        self.categories = {"default": self.default_category}

    def get(self, name):
        return self.categories.get(name)

    def save(self, name):
        category = _Category(name)
        self.categories[name] = category
        return category


class _EntityFactory:
    def create_repo(self, args):
        return type("Repo", (), args)


class _Controller:
    def __init__(self):
        self.categoryDAO = _CategoryDAO()
        self.entity_factory = _EntityFactory()
        self.saved_paths = set()
        self.path_lookup = {}

    def get_repos(self, conditions):
        current_path = conditions["path"]
        existing_path = self.path_lookup.get(current_path)
        if existing_path is None:
            return []
        return [type("Repo", (), {"path": existing_path, "id": 1})]

    def save_repo(self, repo):
        self.saved_paths.add(repo.path)
        self.path_lookup[repo.path] = repo.path
        return type("OperationObject", (), {"success": True, "data": repo})


def test_find_git_repos_under(tmp_path):
    repo1 = tmp_path / "repo1"
    repo1.mkdir()
    (repo1 / ".git").mkdir()

    repo2 = tmp_path / "nested" / "repo2"
    repo2.mkdir(parents=True)
    (repo2 / ".git").write_text("gitdir: /tmp/worktree")

    found_paths = save_subdir_repos_command._find_git_repos_under(str(tmp_path))

    assert sorted(found_paths) == sorted([str(repo1), str(repo2)])


def test_execute_saves_all_repos_with_categories(tmp_path, monkeypatch, capsys):
    repo1 = tmp_path / "repo1"
    repo1.mkdir()
    (repo1 / ".git").mkdir()

    repo2 = tmp_path / "team" / "repo2"
    repo2.mkdir(parents=True)
    (repo2 / ".git").mkdir()

    controller = _Controller()

    monkeypatch.chdir(tmp_path)
    save_subdir_repos_command.execute(["work", "python"], {}, controller)

    output = capsys.readouterr().out

    assert str(repo1.resolve()) in output
    assert str(repo2.resolve()) in output
    assert controller.saved_paths == {str(repo1.resolve()), str(repo2.resolve())}


def test_execute_allows_same_repo_name_when_paths_differ(tmp_path, monkeypatch, capsys):
    repo1 = tmp_path / "team-a" / "shared-name"
    repo1.mkdir(parents=True)
    (repo1 / ".git").mkdir()

    repo2 = tmp_path / "team-b" / "shared-name"
    repo2.mkdir(parents=True)
    (repo2 / ".git").mkdir()

    controller = _Controller()

    monkeypatch.chdir(tmp_path)
    save_subdir_repos_command.execute([], {}, controller)

    output = capsys.readouterr().out

    assert str(repo1.resolve()) in output
    assert str(repo2.resolve()) in output
    assert controller.saved_paths == {str(repo1.resolve()), str(repo2.resolve())}
