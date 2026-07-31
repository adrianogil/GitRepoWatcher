# GitRepoWatcher

CLI utility to register and manage multiple local Git repositories from one place.

## Python compatibility

This project supports **Python 3.9.6+**.

## Dependencies

Install dependencies from `src/python/requirements.txt`:

```bash
pip install -r src/python/requirements.txt
```

Current dependencies:

- `psutil`
- `prompt_toolkit`
- `pytest` (for tests)

## Installation

If you have `gil-install` available:

```bash
cd <GitRepoWatcher-path>
gil-install -i
```

Add the following lines to your shell profile:

```bash
export GIT_REPO_WATCHER_DIR=<path-to-gitrepowatcher>
source $GIT_REPO_WATCHER_DIR/src/bashrc.sh
```

## Usage

```bash
repo-watcher <command> [arguments] [filters]
```

If no command is provided, the tool runs the default mode and lists registered repos.

### Commands

- `-h`, `--help`  
  Show help text.

- `-s`, `--save`  
  Register current repository.  
  Examples:
  ```bash
  repo-watcher -s
  repo-watcher -s -c work personal
  repo-watcher -s "git remote update" default
  ```

- `-ss`  
  Register all Git repositories found under subdirectories of the current path.  
  You can pass category names and they will be assigned to every saved repo.  
  Examples:
  ```bash
  repo-watcher -ss
  repo-watcher -ss work personal
  ```

- `-l`, `--list`  
  List registered repos. You can pass filters (category, id, path).

- `-lc`, `--list-categories`
  List categories.

- `-d`, `--delete`  
  Delete repos matching filters. For safety, a filter is required unless `--all`
  is explicitly provided.

- `-e`, `--edit`  
  Edit repo categories.  
  Supports:
  - `-nc <category...>` to add categories
  - `-rc <category...>` to remove categories

- `-u`, `--update`  
  Run each repo's update command.

- `-up`, `--move-head`
  Move HEAD to upstream when safe (no local unstaged changes / divergence constraints).

- `-p`, `--push`  
  Push local commits to upstream for matching repos.

- `-vc`, `--verify-change`  
  Show repos with unstaged changes or local commits to be pushed.

- `-i`, `--info`  
  Show repo information for current path (or provided filters).

- `-x`, `--fix`  
  Remove entries that point to broken/missing paths.

- `-ld`, `--last-commits`  
  Show latest commit for each matching repo.

- `--stats`  
  Show commit totals per repo.

- `--developer-stats <email>`  
  Show per-repo commit counts for a developer email.

- `-t`, `--today`  
  Show today's commits across matching repos.
  Extra options:
  - `--obsidian` for markdown bullet output
  - `--json <file>` to write report as JSON

- `--exec <command>`  
  Execute a shell command across matching repos.

- `--import <csv_file>`  
  Import repos from CSV (`Path`, `UpdateCommand`, `Category` columns expected).

- `--export <csv_file>`  
  Export repos to CSV.

## Filters

Many commands accept filters after the command arguments:

- Repository id (integer)
- Category name
- Repo path
- `-cs <category...>` to add category filters
- `--path <path>` to filter by path
- `--all` to disable filtering

## Contributing

Feel free to submit PRs.

## Development status

Project is functional but still evolving and could benefit from further refactoring.
