from shell import execute_shell_command


def check_auth(cwd=None):
    execute_shell_command(['gh', 'auth', 'status'], cwd=cwd)


def create_merge_request(cwd, base_branch: str, new_branch: str, release_name: str):
    execute_shell_command([
        'gh', 'pr', 'create',
        '--base', base_branch,
        '--head', new_branch,
        '--title', f'Release {release_name}',
        '--body', f'Automated release PR for {release_name}'
    ], cwd)

def merge_pr(cwd, branch: str, release_name: str):
    execute_shell_command([
        'gh', 'pr', 'merge', branch,
        '--squash',
        '--delete-branch',
        '--subject', f'Merge Release {release_name}'
    ], cwd)

def create_release(cwd, branch: str, release_name: str, notes: str = ""):
    cmd = ['gh', 'release', 'create', release_name, '--target', branch, '--title', release_name]
    if notes:
        cmd.extend(['--notes', notes])
    execute_shell_command(cmd, cwd)

def check_for_open_prs(cwd, branch: str):
    prs = execute_shell_command(
        ['gh', 'pr', 'list', '--state', 'open', '--head', branch],
        cwd=cwd,
        capture_output=True
    )
    return bool(prs)


def check_for_merged_prs(cwd, branch: str):
    prs = execute_shell_command(
        ['gh', 'pr', 'list', '--state', 'merged', '--head', branch],
        cwd=cwd,
        capture_output=True
    )
    return bool(prs)
