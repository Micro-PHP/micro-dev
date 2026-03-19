#!/usr/bin/env python3

import os, argparse, logging, shutil, subprocess, sys, re

from git import InvalidGitRepositoryError

from github import create_merge_request, merge_pr, create_release, check_for_open_prs, check_for_merged_prs, check_auth
from packages import read_packages
from git_commands import create_or_update_branch, get_repository, commit_changes, NothingToCommitException, push_changes, \
    get_changes_to_commit, fetch_tags, fetch_remote, has_remote_branch, has_tag, checkout
from shell import ShellError

logging.basicConfig(level=logging.INFO)

def check_gh_installed() -> bool:
    """Verify that the GitHub CLI is installed."""
    if shutil.which("gh") is None:
        logging.error("GitHub CLI 'gh' not found")
        return False
    try:
        subprocess.run(["gh", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        logging.error(f"GitHub CLI check failed: {e}")
        return False
    return True

def validate_gh_access() -> bool:
    try:
        check_auth()
    except ShellError as e:
        logging.error(f'GitHub CLI authentication check failed: {e}')
        return False
    return True

def compute_next_version(repo):
    """Return the next patch version based on existing tags."""
    versions = []
    pattern = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
    for tag in repo.tags:
        m = pattern.match(tag.name)
        if m:
            versions.append(tuple(map(int, m.groups())))
    if versions:
        major, minor, patch = sorted(versions)[-1]
    else:
        major, minor, patch = 0, 0, 0
    patch += 1
    return f"v{major}.{minor}.{patch}"

def collect_release_notes(repo, base_branch: str) -> str:
    """Collect commit subjects since the last release tag.

    The release flow uses squash merges, so release notes need to be based on
    the commit subjects present on the base branch rather than merge commits.
    """
    tags = [t for t in repo.tags if t.name.startswith("v")]
    if tags:
        last_tag = sorted(tags, key=lambda t: t.commit.committed_datetime)[-1]
        rev_range = f"{last_tag.name}..{base_branch}"
    else:
        rev_range = base_branch
    commits = list(repo.iter_commits(rev_range))
    notes = []
    for commit in reversed(commits):
        subject = commit.message.splitlines()[0].strip()
        if subject:
            notes.append(subject)
    return "\n".join(notes)


def has_unreleased_commits(repo, base_branch: str) -> bool:
    tags = [t for t in repo.tags if t.name.startswith("v")]
    if tags:
        last_tag = sorted(tags, key=lambda t: t.commit.committed_datetime)[-1]
        rev_range = f"{last_tag.name}..{base_branch}"
    else:
        rev_range = base_branch

    return any(True for _ in repo.iter_commits(rev_range, max_count=1))


def preflight_branches(
    packages: dict[str, str],
    release_branch: str | None,
    base_branch: str,
    merge: bool,
    release_current: bool
) -> list[str]:
    failed_packages = []

    for package, folder in packages.items():
        original_directory = os.getcwd()
        os.chdir(folder)
        try:
            repo = get_repository('.')
            fetch_remote(repo)

            if not has_remote_branch(repo, base_branch):
                logging.error(f'Remote base branch `{base_branch}` does not exist in {package}')
                failed_packages.append(package)
                continue

            if release_current:
                continue

            if has_remote_branch(repo, release_branch):
                continue

            if merge and check_for_merged_prs('.', release_branch):
                logging.info(
                    f'Remote release branch `{release_branch}` is absent in {package}, '
                    'but a merged PR exists, allowing release recovery'
                )
                continue

            logging.error(f'Remote release branch `{release_branch}` does not exist in {package}')
            failed_packages.append(package)
        except (ShellError, InvalidGitRepositoryError) as e:
            logging.error(f'Preflight failed for {package}: {e}')
            failed_packages.append(package)
        finally:
            os.chdir(original_directory)

    return failed_packages


def preflight_clean_worktrees(packages: dict[str, str]) -> list[str]:
    failed_packages = []

    for package, folder in packages.items():
        original_directory = os.getcwd()
        os.chdir(folder)
        try:
            repo = get_repository('.')
            if repo.is_dirty(untracked_files=True):
                logging.error(f'Repository for {package} has local changes or untracked files')
                failed_packages.append(package)
        except InvalidGitRepositoryError as e:
            logging.error(f'Worktree preflight failed for {package}: {e}')
            failed_packages.append(package)
        finally:
            os.chdir(original_directory)

    return failed_packages


def preflight_release_tags(packages: dict[str, str], release_name: str, merge: bool, release_current: bool) -> list[str]:
    failed_packages = []

    if not merge and not release_current:
        return failed_packages

    for package, folder in packages.items():
        original_directory = os.getcwd()
        os.chdir(folder)
        try:
            repo = get_repository('.')
            fetch_tags(repo)
            if has_tag(repo, release_name):
                logging.error(f'Release tag `{release_name}` already exists in {package}')
                failed_packages.append(package)
        except (ShellError, InvalidGitRepositoryError) as e:
            logging.error(f'Tag preflight failed for {package}: {e}')
            failed_packages.append(package)
        finally:
            os.chdir(original_directory)

    return failed_packages


def plan_package_action(
    package: str,
    folder: str,
    release_name: str,
    release_branch: str | None,
    base_branch: str,
    merge: bool,
    release_current: bool,
    force_release: bool,
    do_not_release: bool,
    skip_release: bool
) -> tuple[str, bool]:
    original_directory = os.getcwd()
    os.chdir(folder)
    try:
        repo = get_repository('.')
        fetch_remote(repo)

        if not has_remote_branch(repo, base_branch):
            return f'blocked: remote base branch `{base_branch}` is missing', True

        release_branch_exists = has_remote_branch(repo, release_branch) if release_branch else False

        if release_current:
            fetch_tags(repo)
            if has_tag(repo, release_name):
                return f'blocked: release tag `{release_name}` already exists', True
            if repo.is_dirty(untracked_files=True):
                return 'blocked: local changes or untracked files are present', True
            if force_release:
                return f'would force-create release `{release_name}` from `{base_branch}`', False
            if not has_unreleased_commits(repo, base_branch):
                return f'noop: no unreleased commits on `{base_branch}`', False
            return f'would create release `{release_name}` from `{base_branch}`', False

        if merge:
            fetch_tags(repo)
            if has_tag(repo, release_name):
                return f'blocked: release tag `{release_name}` already exists', True
            has_open_pr = check_for_open_prs('.', release_branch)
            has_merged_pr = check_for_merged_prs('.', release_branch)

            if not release_branch_exists and not has_merged_pr:
                return f'blocked: remote release branch `{release_branch}` is missing', True

            if has_open_pr:
                release_version = compute_next_version(repo)
                if skip_release:
                    return f'would merge PR `{release_branch}` and skip release `{release_version}`', False
                if do_not_release:
                    return f'would merge PR `{release_branch}` without creating a release', False
                return f'would merge PR `{release_branch}` and create release `{release_version}`', False

            if has_merged_pr:
                if not has_unreleased_commits(repo, base_branch):
                    return f'noop: merged PR already released on `{base_branch}`', False

                release_version = compute_next_version(repo)
                if skip_release:
                    return f'would skip creating missing release `{release_version}` for merged PR `{release_branch}`', False
                if do_not_release:
                    return f'would not create missing release `{release_version}` because `--no-release` is set', False
                return f'would create missing release `{release_version}` for merged PR `{release_branch}`', False

            return f'noop: no open or merged PR for `{release_branch}`', False

        if repo.is_dirty(untracked_files=True):
            return 'blocked: local changes or untracked files are present', True

        if release_branch_exists:
            if check_for_open_prs('.', release_branch):
                return f'noop: release branch `{release_branch}` and its PR already exist', False
            return f'noop: release branch `{release_branch}` exists remotely but worktree is clean', False

        return 'noop: worktree is clean; nothing would be committed', False
    except (ShellError, InvalidGitRepositoryError) as e:
        return f'blocked: unable to inspect repository state ({e})', True
    finally:
        os.chdir(original_directory)


def preview_actions(
    packages: dict[str, str],
    release_name: str,
    release_branch: str | None,
    base_branch: str,
    merge: bool,
    release_current: bool,
    force_release: bool,
    do_not_release: bool,
    skip_release: bool
) -> list[str]:
    failed_packages = []

    for package, folder in packages.items():
        action, is_blocked = plan_package_action(
            package,
            folder,
            release_name,
            release_branch,
            base_branch,
            merge,
            release_current,
            force_release,
            do_not_release,
            skip_release
        )
        logging.info(f'[{package}] {action}')
        if is_blocked:
            failed_packages.append(package)

    return failed_packages

def main(
    release_name: str,
    branch: str | None,
    base_branch: str,
    config_file: str,
    merge: bool,
    release_current: bool,
    force_release: bool,
    do_not_release: bool,
    skip_release: bool,
    dry_run: bool = False,
    status: bool = False
) -> list[str]:
    if not check_gh_installed():
        sys.exit(1)
    if not validate_gh_access():
        sys.exit(1)
    if not config_file:
        raise ValueError('No config file specified.')

    target_ref = base_branch if release_current else branch
    logging.info(f'Preparing release `{release_name}` on branch `{target_ref}`')
    packages = read_packages(config_file)

    if dry_run or status:
        failed_packages = preview_actions(
            packages,
            release_name,
            branch,
            base_branch,
            merge,
            release_current,
            force_release,
            do_not_release,
            skip_release
        )
        if failed_packages:
            logging.error(f'Preview found blocked packages: {failed_packages}')
        return failed_packages

    failed_packages = preflight_branches(packages, branch, base_branch, merge, release_current)
    if failed_packages:
        logging.error(f'Branch preflight failed for packages: {failed_packages}')
        return failed_packages

    failed_packages = preflight_release_tags(packages, release_name, merge, release_current)
    if failed_packages:
        logging.error(f'Tag preflight failed for packages: {failed_packages}')
        return failed_packages

    if not merge or release_current:
        failed_packages = preflight_clean_worktrees(packages)
        if failed_packages:
            logging.error(f'Worktree preflight failed for packages: {failed_packages}')
            return failed_packages

    failed_packages = []
    for package, folder in packages.items():
        logging.info(f"Processing package {package} in folder {folder}")
        original_directory = os.getcwd()
        os.chdir(folder)
        try:
            if release_current:
                repo = get_repository('.')
                fetch_tags(repo)
                if not force_release and not has_unreleased_commits(repo, base_branch):
                    logging.info(f'No unreleased commits found on `{base_branch}` in {package}, skipping release')
                    continue
                checkout(repo, package, base_branch)
                notes = collect_release_notes(repo, base_branch)
                create_release('.', base_branch, release_name, notes)
            elif merge:
                repo = get_repository('.')
                fetch_tags(repo)
                has_open_pr = check_for_open_prs('.', branch)
                has_merged_pr = check_for_merged_prs('.', branch)

                if not has_open_pr and not has_merged_pr:
                    logging.info(f'No open or merged PR for branch `{branch}` in {package}, skipping merge/release')
                    continue

                if has_open_pr:
                    release_version = compute_next_version(repo)
                    notes = collect_release_notes(repo, base_branch)
                    merge_pr('.', branch, release_version)
                else:
                    if not has_unreleased_commits(repo, base_branch):
                        logging.info(f'No unreleased commits found on `{base_branch}` in {package}, skipping release')
                        continue

                    release_version = compute_next_version(repo)
                    notes = collect_release_notes(repo, base_branch)
                    logging.info(f'PR for branch `{branch}` is already merged in {package}; creating missing release `{release_version}`')

                if skip_release:
                    logging.info(f'Release creation skipped for {package}')
                    continue

                if not do_not_release:
                    create_release('.', base_branch, release_version, notes)
            else:
                repo = get_repository('.')
                files_to_add, files_to_remove = get_changes_to_commit(repo)
                if not bool(files_to_add) and not bool(files_to_remove):
                    logging.info('No changes to commit, skipping')
                    if check_for_open_prs('.', branch):
                        logging.info('btw, PR is already created')
                    continue
                create_or_update_branch(repo, package, branch)
                commit_changes(repo, release_name, package)
                push_changes(repo)
                if not check_for_open_prs('.', branch):
                    create_merge_request('.', base_branch, branch, release_name)
                else:
                    logging.info('PR is already opened')
        except ShellError as e:
            logging.error(f'Shell error: {e}')
            failed_packages.append(package)
        except InvalidGitRepositoryError:
            logging.error(f"Invalid git repository {folder}")
            failed_packages.append(package)
        except NothingToCommitException:
            logging.info('Nothing to commit, skipping pushing and PR creation')
        finally:
            os.chdir(original_directory)

    if 0 < len(failed_packages):
        logging.error(f'The following packages has not been released and should be processed manually: {failed_packages}')

    return failed_packages

       
def run_cli(args=None):
    parser = argparse.ArgumentParser(description='Release script to handle package versions.')
    parser.add_argument('--config', '-c', required=True, help='Path to the config json file')
    parser.add_argument('--merge', action='store_true', help='Merge all open merge requests and create releases')
    parser.add_argument('--release-current', action='store_true', help='Create releases directly from the current base branch without PRs')
    parser.add_argument('--force-release', action='store_true', help='Force release creation in --release-current mode even if no unreleased commits are detected')
    parser.add_argument('--no-release', action='store_true', help="Don't create any release")
    parser.add_argument('--skip-release', '-s', action='store_true', help='Skip creating a release if no PR opened')
    parser.add_argument('--dry-run', action='store_true', help='Show planned actions without mutating repositories or GitHub')
    parser.add_argument('--status', action='store_true', help='Show per-package release status without mutating anything')
    parser.add_argument('--base-branch', '-b', type=str, help='Base branch')
    parser.add_argument('--release-branch', '-r', type=str, help='Release branch to prepare or merge')
    parser.add_argument('release_name', type=str, help='Name of the release')
    app_args = parser.parse_args(args)

    if not app_args.base_branch:
        parser.error('--base-branch is required')
    if not app_args.release_current and not app_args.release_branch:
        parser.error('--release-branch is required')
    if app_args.release_current and app_args.release_branch:
        parser.error('--release-branch cannot be used with --release-current')
    if app_args.release_current and app_args.merge:
        parser.error('--merge cannot be used with --release-current')
    if app_args.release_current and app_args.skip_release:
        parser.error('--skip-release cannot be used with --release-current')
    if app_args.release_current and app_args.no_release:
        parser.error('--no-release cannot be used with --release-current')
    if app_args.force_release and not app_args.release_current:
        parser.error('--force-release can only be used with --release-current')

    config_file_path = os.path.abspath(app_args.config)
    working_dir = os.path.dirname(config_file_path)
    os.chdir(working_dir)

    failed_packages = main(
        app_args.release_name,
        app_args.release_branch,
        app_args.base_branch,
        config_file_path,
        app_args.merge,
        app_args.release_current,
        app_args.force_release,
        app_args.no_release,
        app_args.skip_release,
        app_args.dry_run,
        app_args.status
    )

    if failed_packages:
        sys.exit(1)


if __name__ == '__main__':
    run_cli()
