# Add the following lines to your bashrc:
# export GIT_REPO_WATCHER_DIR=<path-to>/GitRepoWatcher
# source $GIT_REPO_WATCHER_DIR/src/bashrc.sh


MAIN_SCRIPT=gitrepowatcher.py
OLD_SCRIPT=gitrepowatcher_old.py

alias repo-watcher='python2 $GIT_REPO_WATCHER_DIR/$MAIN_SCRIPT'
alias rw='python2 $GIT_REPO_WATCHER_DIR/$MAIN_SCRIPT'
alias rwc='rw -c'


alias rw-old='python2 $GIT_REPO_WATCHER_DIR/$OLD_SCRIPT'

function rws()
{
    python2 $GIT_REPO_WATCHER_DIR/src/$MAIN_SCRIPT $* | less    
}