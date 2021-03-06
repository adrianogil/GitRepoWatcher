# GitRepoWatcher
Python scripts to manage multiple git repos

# Command line options

Save a repo with category 'default' and update command as 'git remote update'

```
repo-watcher -s
```

Save a repo with category 'default'

```
repo-watcher -s <category>
```

Save a repo with a specific update command and a category
```
repo-watcher -s <category> <update-command>
```

Update all saved repos. Each registered repo will be updated using their corresponding update command.
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

Delete all stored data
```
repo-watcher --delete-all
```


Verify changes in repos
```
repo-watcher -c
```


Get info about current path
```
repo-watcher -i
```

Get commit stats
```
repo-watcher --stats
```

Get commits from today
```
repo-watcher --today
```

## Planned features
- Refactoring code using DAO
- More than one category for repo
- Add a excluding category
- Add few features similar to [https://github.com/kamranahmedse/git-standup](git-standup)

## Installation

In case you have gil-install command, you just need to type:

```
cd <Gitrepowatcher-path>
gil-install -i
```

Add the following lines to your bashrc:
```
export GIT_REPO_WATCHER_DIR=<path-to-gitrepowatcher>
source $GIT_REPO_WATCHER_DIR/src/bashrc.sh
```

## Contributing

Feel free to submit PRs. I will do my best to review and merge them if I consider them essential.

## Development status

This is a very alpha software. The code was written with no consideration of coding standards and architecture. A refactoring would do it good...