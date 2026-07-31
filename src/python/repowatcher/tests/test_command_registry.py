from types import SimpleNamespace

import pytest

import repowatcher.gitrepocontroller as gitrepocontroller
from repowatcher.commands import (
    list_categories_command,
    list_repos_command,
    move_head_command,
    push_commits_command,
    update_batch_command,
)
from repowatcher.commands.available_commands import get_available_commands
from repowatcher.gitrepocontroller import GitRepoController


def test_available_command_flags_are_unique():
    command_flags = [
        flag
        for command in get_available_commands()
        for flag in command.get_cmd_flags()
    ]

    assert len(command_flags) == len(set(command_flags))


def test_commands_use_unambiguous_long_aliases():
    assert list_categories_command.get_cmd_flags() == [
        "-lc",
        "--list-categories",
    ]
    assert move_head_command.get_cmd_flags() == ["-up", "--move-head"]


def test_registry_maps_resolved_aliases_to_intended_commands():
    controller = GitRepoController.__new__(GitRepoController)

    commands = controller.get_commands()

    assert commands["--list"] is list_repos_command.execute
    assert commands["--list-categories"] is list_categories_command.execute
    assert commands["--update"] is update_batch_command.execute
    assert commands["--move-head"] is move_head_command.execute
    assert commands["-p"] is push_commits_command.execute
    assert "--path" not in commands


def test_controller_rejects_duplicate_command_flags(monkeypatch):
    first_command = SimpleNamespace(
        get_cmd_flags=lambda: ["--duplicate"],
        execute=lambda *_: None,
    )
    second_command = SimpleNamespace(
        get_cmd_flags=lambda: ["--duplicate"],
        execute=lambda *_: None,
    )
    monkeypatch.setattr(
        gitrepocontroller,
        "get_available_commands",
        lambda: [first_command, second_command],
    )
    controller = GitRepoController.__new__(GitRepoController)

    with pytest.raises(ValueError, match="Duplicate command flag: --duplicate"):
        controller.get_commands()


def test_controller_rejects_command_alias_that_conflicts_with_option(monkeypatch):
    command = SimpleNamespace(
        get_cmd_flags=lambda: ["--path"],
        execute=lambda *_: None,
    )
    monkeypatch.setattr(
        gitrepocontroller,
        "get_available_commands",
        lambda: [command],
    )
    controller = GitRepoController.__new__(GitRepoController)

    with pytest.raises(
        ValueError,
        match="Command flag conflicts with option flag: --path",
    ):
        controller.get_commands()
