from repowatcher.commands import execute_command


class _Repo:
    id = 7
    name = "repo"
    path = "/tmp/repo with spaces"


class _Controller:
    def get_search_conditions(self, args, extra_args):
        assert args == ["category"]
        assert extra_args == {"--all": True}
        return {"category": "value"}

    def get_repos(self, search_conditions):
        assert search_conditions == {"category": "value"}
        return [_Repo()]


def test_execute_runs_command_args_in_repo_cwd(monkeypatch, capsys):
    def fake_check_output(cmd, cwd):
        assert cmd == ["git", "status", "--short"]
        assert cwd == "/tmp/repo with spaces"
        return b"M file.txt\n"

    monkeypatch.setattr("subprocess.check_output", fake_check_output)

    execute_command.execute(["git status --short", "category"], {"--all": True}, _Controller())

    assert "M file.txt" in capsys.readouterr().out
