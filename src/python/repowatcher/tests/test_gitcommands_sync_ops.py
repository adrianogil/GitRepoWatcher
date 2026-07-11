import repowatcher.gitcommands as gitcommands


class _Result:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_rebase_returns_failure_payload_without_exceptions(monkeypatch):
    def fake_run(cmd, cwd, capture_output, text):
        assert cmd == ["git", "rebase"]
        assert cwd == "/tmp/repo"
        assert capture_output is True
        assert text is True
        return _Result(returncode=1, stdout="", stderr="conflict")

    monkeypatch.setattr("subprocess.run", fake_run)

    result = gitcommands.rebase("/tmp/repo")

    assert result["ok?"] is False
    assert result["returncode"] == 1
    assert "conflict" in result["output"]


def test_remote_update_returns_combined_output(monkeypatch):
    def fake_run(cmd, cwd, capture_output, text):
        assert cmd == ["git", "remote", "update"]
        return _Result(returncode=0, stdout="Fetching", stderr="warn")

    monkeypatch.setattr("subprocess.run", fake_run)

    output = gitcommands.remote_update("/tmp/repo")

    assert output == "Fetching\nwarn"


def test_get_git_root_runs_git_with_cwd(monkeypatch):
    calls = []

    def fake_call(cmd, cwd, stdout, stderr):
        calls.append(("call", cmd, cwd))
        return 0

    def fake_check_output(cmd, cwd):
        calls.append(("check_output", cmd, cwd))
        return b"/tmp/repo with spaces"

    monkeypatch.setattr("subprocess.call", fake_call)
    monkeypatch.setattr("subprocess.check_output", fake_check_output)

    root = gitcommands.get_git_root("/tmp/repo with spaces/subdir")

    assert root == "/tmp/repo with spaces"
    assert calls == [
        ("call", ["git", "branch"], "/tmp/repo with spaces/subdir"),
        ("check_output", ["git", "rev-parse", "--show-toplevel"], "/tmp/repo with spaces/subdir"),
    ]


def test_get_unstaged_files_counts_numstat_lines_without_shell(monkeypatch):
    def fake_check_output(cmd, cwd):
        assert cmd == ["git", "diff", "--numstat"]
        assert cwd == "/tmp/repo with spaces"
        return b"1\t0\tfile one.txt\n2\t1\tfile two.txt\n\n"

    monkeypatch.setattr("subprocess.check_output", fake_check_output)

    assert gitcommands.get_unstaged_files("/tmp/repo with spaces") == "2"


def test_author_log_query_keeps_author_as_single_arg(monkeypatch):
    def fake_check_output(cmd, cwd):
        assert cmd == [
            "git",
            "log",
            "--author=Dev User <dev@example.com>",
            "--pretty=oneline",
        ]
        assert cwd == "/tmp/repo with spaces"
        return b"abc Commit one\n"

    monkeypatch.setattr("subprocess.check_output", fake_check_output)

    assert gitcommands.get_commits_by_author("/tmp/repo with spaces", "Dev User <dev@example.com>") == 1
