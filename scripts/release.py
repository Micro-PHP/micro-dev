#!/usr/bin/env python3

import os, argparse, logging

from git import InvalidGitRepositoryError

from github import create_merge_request, merge_pr, create_release, check_for_open_prs
from git_shell import get_current_git_branch
from packages import read_packages
from git_commands import create_or_update_branch, get_repository, commit_changes, NothingToCommitException, push_changes, \
    BranchNotActiveError, get_changes_to_commit
from shell import ShellError

logging.basicConfig(level=logging.INFO)

def main(
    release_name: str,
    branch: str,
    base_branch: str,
    config_file: str,
    merge: bool,
    do_not_release: bool,
    skip_release: bool
):
    if not config_file:
        raise ValueError('No config file specified.')

    logging.info(f'Preparing release `{release_name}` on branch `{branch}`')
    packages = read_packages(config_file)

    failed_packages = []
    for package, folder in packages.items():
        logging.info(f"Processing package {package} in folder {folder}")
        original_directory = os.getcwd()
        os.chdir(folder)
        try:
            if merge:
                if check_for_open_prs('.', branch):
                    merge_pr('.', branch, release_name)
                elif skip_release:
                    continue
                if not do_not_release:
                    create_release('.', base_branch, release_name)
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
        except BranchNotActiveError:
            logging.warning(f'Branch does exist but is not active. Please manually switch to branch `{branch}`')
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

       
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Release script to handle package versions.')
    parser.add_argument('--config', '-c', required=True, help='Path to the config json file')
    parser.add_argument('--merge', action='store_true', help='Merge all open merge requests and create releases')
    parser.add_argument('--no-release', action='store_true', help='Don\'t create any release')
    parser.add_argument('--skip-release', '-s', action='store_true', help='Skip creating a release if no PR opened')
    parser.add_argument('--base-branch', '-b', type=str, help='Base branch')
    parser.add_argument('release_name', type=str, help='Name of the release')
    app_args = parser.parse_args()

    config_file_path = os.path.abspath(app_args.config)
    working_dir = os.path.dirname(config_file_path)
    os.chdir(working_dir)

    main(
        app_args.release_name,
        get_current_git_branch(),
        app_args.base_branch,
        config_file_path,
        app_args.merge,
        app_args.no_release,
        app_args.skip_release
    )