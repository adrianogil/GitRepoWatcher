# GitRepoWatcher
Python scripts to manage multiple git repos

# Command line options

Save a repo with category 'default' and update command as 'git remote update'

```
repo-watcher -s
```

Save a repo with category 'default'

```
repo-watcher -s <update-command>
```

Save a repo with a specific update command and a category
```
repo-watcher -s <update-command> <category>
```

Update all saved repos. It will can the update command of each registered repo.
```
repo-watcher --update [<category>]
```

```
repo-watcher -u [<category>]
```


Move HEAD to upstream in all saved repos.
```
repo-watcher -up [<category>]
```

Delete a saved repo.
```
repo-watcher -d <id>
```

Delete current folder from saved repos.
```
repo-watcher -d
```


## Planned features
-

## Installation

Add the following lines to your bashrc:
```
export GIT_REPO_WATCHER_DIR=<path-to-gitrepowatcher>
source $GIT_REPO_WATCHER_DIR/src/bashrc.sh
```
(WIP I am going to create a better setup)

## Contributing

Feel free to submit PRs. I will do my best to review and merge them if I consider them essential.

## Development status

This is a very alpha software. The code was written with no consideration of coding standards and architecture. A refactoring would do it good...