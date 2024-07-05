#!/usr/bin/env python3

import os, argparse, logging

from git import Repo, InvalidGitRepositoryError

from github import create_merge_request, merge_pr, create_release, check_for_open_prs
from git_shell import get_current_git_branch, PackageBranchExistError
from packages import read_packages

logging.basicConfig(level=logging.INFO)

def fetch(func):
    def wrapper(repository: Repo, package: str, *args, **kwargs):
        logging.info(f'Fetching from remote origin {repository.remotes.origin.url} to {package}')
        repository.git.fetch()
        return func(repository, package, *args, **kwargs)
    return wrapper

@fetch
def create_or_update_branch(repository: Repo, package: str, branch_name: str):
    if branch_name in repository.heads:
        logging.info(f'Branch {branch_name} exists.')
        if repository.active_branch.name != branch_name:
            raise NameError(f'Branch {branch_name} already exists but is not active.')
        logging.info(f"Repository is already on branch '{branch_name}'")
    else:
        repository.create_head(branch_name)

def commit_changes(repository: Repo, release_name: str, package: str):
    untracked_files = repository.untracked_files
    unstaged_files = [item.a_path for item in repository.index.diff(None)]
    staged_files = [item.a_path for item in repository.index.diff('HEAD')]
    all_files_to_add = untracked_files + unstaged_files + staged_files
    if not all_files_to_add:
        logging.info('No changes to commit.')
        return
    repository.index.add(all_files_to_add)
    repository.index.commit(f'Update {release_name} for {package}')

def push_changes(repository: Repo):
    current_branch = repository.active_branch
    repository.git.push('--set-upstream', repository.remote().name, current_branch.name)
    logging.info(f'Pushed changes to {current_branch.name}')

def get_repository(directory: str) -> Repo:
    return Repo(directory)

def main(release_name, branch, config_file, merge):
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
            repo = get_repository('.')
            create_or_update_branch(repo, package, branch)
            commit_changes(repo, release_name, package)
            push_changes(repo)
            if not check_for_open_prs('.', branch):
                create_merge_request('.', '2.x', branch, release_name)
            else:
                logging.info('MR is already opened')
        except InvalidGitRepositoryError:
            logging.error(f"Invalid git repository {folder}")
            failed_packages.append(package)
        finally:
            os.chdir(original_directory)

        # try:
        #     if merge:
        #         pass
        #         # if check_for_open_prs(folder, branch):
        #         #     merge_pr(folder, release_name)
        #         #     create_release(folder, branch, release_name)
        #     else:
        #         create_or_update_branch(folder, branch)
        #         commit_changes(folder, f'Release {release_name}')
        #         # push_changes(folder, branch)
        #         # create_merge_request(folder, branch, release_name)
        # except PackageBranchExistError:
        #     failed_packages.append(package)
        return # temporally for testing purposes

    if 0 < len(failed_packages):
        logging.error(f'The following packages has not been released and should be processed manually: {failed_packages}')

       
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Release script to handle package versions.')
    parser.add_argument('--config', '-c', required=True, help='Path to the config json file')
    parser.add_argument('release_name', type=str, help='Name of the release')
    parser.add_argument('--merge', action='store_true', help='Merge all open merge requests and create releases')
    app_args = parser.parse_args()

    config_file_path = os.path.abspath(app_args.config)
    working_dir = os.path.dirname(config_file_path)
    os.chdir(working_dir)

    main(app_args.release_name, get_current_git_branch(), config_file_path, False) # app_args.merge
