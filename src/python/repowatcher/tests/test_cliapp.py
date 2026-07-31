import sys

import pytest

from repowatcher.utils import flags
from repowatcher.utils.cliapp import CliApp


class _FakeController:
    def __init__(self, commands):
        self.commands = commands

    def get_commands(self):
        return self.commands


@pytest.fixture(autouse=True)
def reset_parsed_flags():
    flags.flags.clear()
    yield
    flags.flags.clear()


def test_run_without_arguments_dispatches_default_command(monkeypatch):
    calls = []
    controller = _FakeController(
        {
            "no-args": lambda: calls.append("default"),
        }
    )
    monkeypatch.setattr(sys, "argv", ["repo-watcher"])

    CliApp(controller).run()

    assert calls == ["default"]


@pytest.mark.parametrize("command_flag", ["-k", "--known"])
def test_run_dispatches_registered_alias_and_forwards_parsed_arguments(
    monkeypatch,
    command_flag,
):
    calls = []

    def execute(args, extra_args, controller):
        calls.append((args, extra_args, controller))

    controller = _FakeController(
        {
            "-k": execute,
            "--known": execute,
        }
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "repo-watcher",
            command_flag,
            "first",
            "-7",
            "--filter",
            "work",
            "personal",
        ],
    )

    CliApp(controller).run()

    assert calls == [
        (
            ["first", "-7"],
            {
                command_flag: ["first", "-7"],
                "--filter": ["work", "personal"],
            },
            controller,
        )
    ]


def test_run_reports_unknown_command_without_dispatching(monkeypatch, capsys):
    calls = []
    controller = _FakeController(
        {
            "--known": lambda *args: calls.append(args),
        }
    )
    monkeypatch.setattr(sys, "argv", ["repo-watcher", "--unknown", "value"])

    CliApp(controller).run()

    assert calls == []
    assert capsys.readouterr().out == "Command not found\n"


def test_run_reports_when_controller_has_no_matching_commands(monkeypatch, capsys):
    controller = _FakeController({})
    monkeypatch.setattr(sys, "argv", ["repo-watcher", "--known"])

    CliApp(controller).run()

    assert capsys.readouterr().out == "Command not found\n"


def test_run_refuses_to_dispatch_multiple_commands(monkeypatch, capsys):
    calls = []

    def execute(*args):
        calls.append(args)

    controller = _FakeController(
        {
            "--first": execute,
            "--second": execute,
        }
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["repo-watcher", "--first", "one", "--second", "two"],
    )

    CliApp(controller).run()

    assert calls == []
    assert capsys.readouterr().out == (
        "Only one command can be specified: --first, --second\n"
    )
