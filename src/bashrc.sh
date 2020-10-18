# Add the following lines to your bashrc:
# export GIT_REPO_WATCHER_DIR=<path-to>/GitRepoWatcher
# source $GIT_REPO_WATCHER_DIR/src/bashrc.sh

if [ -z "$REPOWATCHER_PYTHON_PATH" ];
then
    export REPOWATCHER_PYTHON_PATH=$GIT_REPO_WATCHER_DIR/python/
    export PYTHONPATH=$REPOWATCHER_PYTHON_PATH:$PYTHONPATH
fi

alias repo-watcher='python3 -m repowatcher'
alias rw='python3 -m repowatcher'
alias rwc='rw -c'


function rws()
{
    python3 -m repowatcher $* | less
}