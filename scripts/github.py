from shell import execute_shell_command


def create_merge_request(cwd, base_branch: str, new_branch: str, release_name: str):
    execute_shell_command(f'gh pr create --base {base_branch} --head {new_branch} --title "Release {release_name}" --body "Automated release PR for {release_name}"', cwd)

def merge_pr(cwd, branch: str, release_name: str):
    execute_shell_command(f'gh pr merge {branch} --squash --delete-branch --subject "Merge Release {release_name}"', cwd)

def create_release(cwd, branch: str, release_name: str):
    execute_shell_command(f'gh release create {release_name} --target {branch} --title "{release_name}" --notes "Release notes for {release_name}"', cwd)

def check_for_open_prs(cwd, branch: str):
    prs = execute_shell_command(f'gh pr list --state open --head {branch}', cwd=cwd, capture_output=True)
    return bool(prs)

