#!/usr/bin/env python3

import os, logging, argparse

from git import Repo, InvalidGitRepositoryError

from exceptions import MissingBranchError
from packages import read_packages
from packagist import get_repository_link
from git_shell import get_current_git_branch

logging.basicConfig(level=logging.INFO)

def ensure_folder_exists(func):
    def wrapper(package_directory, *args, **kwargs):
        if not os.path.exists(package_directory):
            logging.info(f"Creating folder {package_directory}")
            os.makedirs(package_directory)
        return func(package_directory, *args, **kwargs)
    return wrapper

def change_directory(func):
    def wrapper(package_directory, *args, **kwargs):
        original_directory = os.getcwd()
        os.chdir(package_directory)
        try:
            return func(package_directory, *args, **kwargs)
        finally:
            os.chdir(original_directory)
    return wrapper

@ensure_folder_exists
@change_directory
def init_repository(package_directory, package_repo) -> Repo:
    try:
        repository = Repo('.')
    except InvalidGitRepositoryError:
        logging.info(f'Initializing git repository in {package_directory}')
        repository = Repo.init('.')
    if 'origin' not in repository.remotes:
        logging.info(f'Adding remote origin {package_repo} to {package_directory}')
        repository.create_remote('origin', package_repo)
    # if repository.remotes.origin.url != package_repo:
    #     logging.info(f'Updating remote origin {package_repo} to {package_directory}')
    #     repository.remotes.origin.url = package_repo
    return repository

def fetch(func):
    def wrapper(repository, *args, **kwargs):
        package_name = repository.remotes.origin.url.split('/')[-1].split('.')[0]
        logging.info(f'Fetching from remote origin {repository.remotes.origin.url} to {package_name}')
        repository.git.fetch()
        return func(repository, *args, **kwargs)
    return wrapper

def ensure_already_branch(func):
    def wrapper(repository, branch):
        if repository.active_branch.name == branch:
            package_name = repository.remotes.origin.url.split('/')[-1].split('.')[0]
            logging.info(f'Repository is already on {branch} branch for {package_name}')
            return
        return func(repository, branch)
    return wrapper

@fetch
@ensure_already_branch
def checkout(repository, branch):
    package_name = repository.remotes.origin.url.split('/')[-1].split('.')[0]
    try:
        logging.info(f'Checking out branch {branch} in {package_name}')
        repository.git.checkout('-f', branch)
    except InvalidGitRepositoryError:
        logging.info(f'Branch {branch} does not exist in {package_name}')
        raise MissingBranchError(f'Branch {branch} does not exist in {package_name}')

def main(branch, config_file):
    if not config_file:
        raise ValueError('No config file specified.')

    packages_with_missing_branches = []
    packages = read_packages(config_file)

    for package, folder in packages.items():
        repository = init_repository(folder, get_repository_link(package))
        try:
            checkout(repository, branch)
        except MissingBranchError:
            packages_with_missing_branches.append(package)
        except Exception as e:
            logging.error(e)

    if 0 < len(packages_with_missing_branches):
        print(f'The following packages do not have the {branch} branch: {packages_with_missing_branches}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to manage git multi-repositories.')
    parser.add_argument('--config', '-c', required=True, help='Path to the config json file')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug logging')
    app_args = parser.parse_args()

    if app_args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    config_file_path = os.path.abspath(app_args.config)
    working_dir = os.path.dirname(config_file_path)
    os.chdir(working_dir)

    main(get_current_git_branch(), os.path.basename(config_file_path))
