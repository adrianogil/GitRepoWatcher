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
