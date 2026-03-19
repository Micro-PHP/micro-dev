import os, logging

from git import Repo, InvalidGitRepositoryError, GitCommandError

class NothingToCommitException(Exception):
    pass

class MissingBranchError(Exception):
    pass

class BranchNotActiveError(Exception):
    pass

class RepositoryDirtyError(Exception):
    pass

class TagAlreadyExistsError(Exception):
    pass

class MissingBaseBranchError(Exception):
    pass


def has_commits(repository: Repo) -> bool:
    try:
        return repository.head.is_valid()
    except (TypeError, ValueError):
        return False


def is_unborn_repository_with_worktree(repository: Repo) -> bool:
    return not has_commits(repository) and bool(repository.untracked_files)


def attach_head_to_branch(repository: Repo, branch_name: str, upstream_branch: str | None = None):
    repository.git.symbolic_ref('HEAD', f'refs/heads/{branch_name}')
    logging.info(f"Attached repository HEAD to local branch '{branch_name}' without changing files")

    if upstream_branch:
        with repository.config_writer() as config:
            config.set_value(f'branch "{branch_name}"', 'remote', repository.remote().name)
            config.set_value(f'branch "{branch_name}"', 'merge', f'refs/heads/{upstream_branch}')
        logging.info(f"Configured branch '{branch_name}' to track '{upstream_branch}'")


def checkout_unborn_repository_to_remote_branch(repository: Repo, branch_name: str, remote_ref):
    if branch_name not in repository.heads:
        local_branch = repository.create_head(branch_name, remote_ref.commit)
        local_branch.set_tracking_branch(remote_ref)
    repository.heads[branch_name].checkout(force=True)
    repository.git.reset('--hard', remote_ref.name)
    logging.info(f"Checked out branch '{branch_name}' from remote '{remote_ref.name}' for unborn repository")

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
        repository.heads[branch_name].checkout()
        logging.info(f"Switched to existing branch '{branch_name}'")
        return

    remote_branch = next((ref for ref in repository.remotes.origin.refs if ref.remote_head == branch_name), None)
    if remote_branch:
        new_branch = repository.create_head(branch_name, remote_branch.commit)
        new_branch.set_tracking_branch(remote_branch)
        new_branch.checkout()
        logging.info(f"Tracking branch '{branch_name}' created and switched to.")
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

def fetch_tags(repository: Repo):
    repository.git.fetch('--tags')
    logging.info('Fetched remote tags')

def has_tag(repository: Repo, tag_name: str) -> bool:
    return any(tag.name == tag_name for tag in repository.tags)

def fetch_remote(repository: Repo):
    repository.git.fetch('origin')
    logging.info('Fetched remote branches')

def has_remote_branch(repository: Repo, branch_name: str) -> bool:
    return any(ref.remote_head == branch_name for ref in repository.remotes.origin.refs)


@fetch
def create_branch_from_remote(
    repository: Repo,
    package: str,
    target_branch: str,
    from_branch: str,
    push_missing_branch: bool = False
):
    if repository.is_dirty(untracked_files=True) and not is_unborn_repository_with_worktree(repository):
        raise RepositoryDirtyError(
            f'Repository for {package} has local changes; refusing to create branch automatically.'
        )

    remote_target = next((ref for ref in repository.remotes.origin.refs if ref.remote_head == target_branch), None)
    if is_unborn_repository_with_worktree(repository):
        if remote_target:
            checkout_unborn_repository_to_remote_branch(repository, target_branch, remote_target)
            return

        remote_base = next((ref for ref in repository.remotes.origin.refs if ref.remote_head == from_branch), None)
        if not remote_base:
            raise MissingBaseBranchError(
                f'Base branch {from_branch} does not exist in {package}; cannot create {target_branch}'
            )

        checkout_unborn_repository_to_remote_branch(repository, target_branch, remote_base)
        if push_missing_branch:
            repository.git.push('--set-upstream', repository.remote().name, target_branch)
            repository.git.fetch()
            repository.heads[target_branch].set_tracking_branch(repository.remotes.origin.refs[target_branch])
            logging.info(f"Pushed missing branch '{target_branch}' to origin for {package}")
        return

    if remote_target:
        if target_branch not in repository.heads:
            local_branch = repository.create_head(target_branch, remote_target.commit)
            local_branch.set_tracking_branch(remote_target)
        repository.heads[target_branch].checkout()
        logging.info(f"Checked out existing remote branch '{target_branch}' for {package}")
        return

    remote_base = next((ref for ref in repository.remotes.origin.refs if ref.remote_head == from_branch), None)
    if not remote_base:
        raise MissingBaseBranchError(
            f'Base branch {from_branch} does not exist in {package}; cannot create {target_branch}'
        )

    if target_branch in repository.heads:
        local_branch = repository.heads[target_branch]
    else:
        local_branch = repository.create_head(target_branch, remote_base.commit)
    local_branch.checkout()
    logging.info(f"Created local branch '{target_branch}' from '{from_branch}' for {package}")

    if push_missing_branch:
        repository.git.push('--set-upstream', repository.remote().name, local_branch.name)
        repository.git.fetch()
        local_branch.set_tracking_branch(repository.remotes.origin.refs[target_branch])
        logging.info(f"Pushed missing branch '{target_branch}' to origin for {package}")

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
def init_repository(package_directory: str, package_repo: str, branch_name: str | None = None) -> Repo:
    """Initializes a package repository and synchronizes it with ``origin``.

    The function fetches remote history from ``origin`` and prepares local
    tracking for the requested branch when available. It does not hard reset or
    overwrite local changes.
    """
    try:
        repository = Repo('.')
    except InvalidGitRepositoryError:
        logging.info(f'Initializing git repository in {package_directory}')
        repository = Repo.init('.')
    if 'origin' not in repository.remotes:
        logging.info(f'Adding remote origin {package_repo} to {package_directory}')
        repository.create_remote('origin', package_repo)

    origin = repository.remotes.origin
    origin.fetch()

    if branch_name:
        remote_branch = next((ref for ref in origin.refs if ref.remote_head == branch_name), None)
        if remote_branch and branch_name not in repository.heads:
            branch = repository.create_head(branch_name, remote_branch.commit)
            branch.set_tracking_branch(remote_branch)
            logging.info(f"Tracking branch '{branch_name}' created during initialization")

    if repository.is_dirty(untracked_files=True) and not is_unborn_repository_with_worktree(repository):
        logging.warning(f'Repository {package_directory} is not clean after initialization')

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
        remote_branch = next((ref for ref in repository.remotes.origin.refs if ref.remote_head == branch), None)
        if is_unborn_repository_with_worktree(repository):
            if not remote_branch:
                raise MissingBranchError(f'Branch {branch} does not exist in {package}')
            checkout_unborn_repository_to_remote_branch(repository, branch, remote_branch)
            return

        if repository.is_dirty(untracked_files=True):
            raise RepositoryDirtyError(
                f'Repository for {package} has local changes; refusing to switch branches automatically.'
            )

        logging.info(f'Checking out branch {branch} in {package}')
        if branch in repository.heads:
            repository.heads[branch].checkout()
            return

        if remote_branch:
            local_branch = repository.create_head(branch, remote_branch.commit)
            local_branch.set_tracking_branch(remote_branch)
            local_branch.checkout()
            return

        raise MissingBranchError(f'Branch {branch} does not exist in {package}')
    except (InvalidGitRepositoryError, GitCommandError):
        logging.info(f'Branch {branch} does not exist in {package}')
        raise MissingBranchError(f'Branch {branch} does not exist in {package}')
