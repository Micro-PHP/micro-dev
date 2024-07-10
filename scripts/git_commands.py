
import os, logging

from git import Repo, InvalidGitRepositoryError

class NothingToCommitException(Exception):
    pass

class MissingBranchError(Exception):
    pass

class BranchNotActiveError(Exception):
    pass

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
            raise BranchNotActiveError(f'Branch {branch_name} already exists but is not active.')
        logging.info(f"Repository is already on branch '{branch_name}'")
    else:
        new_branch = repository.create_head(branch_name)
        new_branch.checkout()
        logging.info(f'Branch {new_branch.name} created and switched to.')

def get_changes_to_commit(repository: Repo):
    untracked_files = repository.untracked_files
    unstaged_files = [item.a_path for item in repository.index.diff(None) if item.change_type != 'D']
    staged_files = [item.a_path for item in repository.index.diff('HEAD') if item.change_type != 'D']
    deleted_files = [item.a_path for item in repository.index.diff(None) if item.change_type == 'D']
    return untracked_files + unstaged_files + staged_files, deleted_files

def commit_changes(repository: Repo, release_name: str, package: str):
    files_to_commit, files_to_remove = get_changes_to_commit(repository)
    logging.debug(f'Files to commit: {files_to_commit}')
    logging.debug(f'Files to remove: {files_to_remove}')

    if not files_to_commit and not files_to_remove:
        logging.info('No changes to commit.')
        raise NothingToCommitException('No changes to commit.')

    if files_to_commit:
        repository.index.add(files_to_commit)
    if files_to_remove:
        repository.index.remove(files_to_remove)

    commit_message = f'Update {release_name} for {package}'
    logging.info(f'Committing changes with message: {commit_message}')
    repository.index.commit(commit_message)

def push_changes(repository: Repo):
    current_branch = repository.active_branch
    repository.git.push('--set-upstream', repository.remote().name, current_branch.name)
    logging.info(f'Pushed changes to {current_branch.name}')

def get_repository(directory: str) -> Repo:
    return Repo(directory)

def ensure_folder_exists(func):
    def wrapper(package_directory: str, *args, **kwargs):
        if not os.path.exists(package_directory):
            logging.info(f"Creating folder {package_directory}")
            os.makedirs(package_directory)
        return func(package_directory, *args, **kwargs)
    return wrapper

def change_directory(func):
    def wrapper(package_directory: str, *args, **kwargs):
        original_directory = os.getcwd()
        os.chdir(package_directory)
        try:
            return func(package_directory, *args, **kwargs)
        finally:
            os.chdir(original_directory)
    return wrapper

@ensure_folder_exists
@change_directory
def init_repository(package_directory: str, package_repo: str) -> Repo:
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

def update_repository_remote_link(repository: Repo, remote_name: str, remote_url: str) -> None:
    try:
        remote = repository.remote(remote_name)
        old_urls = remote.urls
        if remote_url in old_urls:
            logging.info(f'Remote URL is already {remote_url}')
            return
        remote.set_url(remote_url)
        logging.info(f'Remote URL is set from {list(old_urls)} to {remote_url}')
    except ValueError as e:
        logging.warning(f'Remote URL cannot be changed because {e}')
        raise e
    except Exception as e:
        logging.error(f'Error updating remote URL {remote_url}: {e}')
        raise e

def ensure_already_branch(func):
    def wrapper(repository: Repo, package: str, branch: str, *args, **kwargs):
        if repository.active_branch.name == branch:
            logging.info(f'Repository is already on {branch} branch for {package}')
            return
        return func(repository, package, branch, *args, **kwargs)
    return wrapper

@fetch
@ensure_already_branch
def checkout(repository: Repo, package: str, branch: str):
    try:
        logging.info(f'Checking out branch {branch} in {package}')
        repository.git.checkout('-f', branch)
    except InvalidGitRepositoryError:
        logging.info(f'Branch {branch} does not exist in {package}')
        raise MissingBranchError(f'Branch {branch} does not exist in {package}')
