from shell import execute_shell_command


class PackageBranchExistError(Exception):
    pass


def get_current_git_branch(cwd=None):
    current_branch = execute_shell_command('git branch --show-current', cwd=cwd, capture_output=True)
    return current_branch

def fetch_repo(cwd):
    execute_shell_command('git fetch', cwd)

def create_or_update_branch(cwd, branch: str):
    fetch_repo(cwd)
    branches = execute_shell_command('git branch -a', cwd=cwd, capture_output=True)
    if f'remotes/origin/{branch}' in branches:
        execute_shell_command(f'git push -f', cwd)
    else:
        execute_shell_command(f'git checkout -b {branch}', cwd)

def commit_changes(cwd, message='Release changes'):
    execute_shell_command('git add .', cwd)
    execute_shell_command(f'git commit -am "{message}"', cwd)

def push_changes(cwd, new_branch: str):
    execute_shell_command(f'git push origin {new_branch}', cwd)
