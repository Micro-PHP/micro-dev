#!/usr/bin/env python3

import os, logging, argparse

from packages import read_packages
from packagist import get_repository_link
from git_shell import get_current_git_branch
from git_commands import checkout, init_repository, MissingBranchError, RepositoryDirtyError, \
    create_branch_from_remote, MissingBaseBranchError

logging.basicConfig(level=logging.INFO)

def main(branch, config_file, from_branch=None, push_missing_branches=False):
    if not config_file:
        raise ValueError('No config file specified.')

    packages = read_packages(config_file)

    packages_with_missing_branches = []
    packages_with_missing_base_branches = []
    packages_with_dirty_repositories = []
    for package, folder in packages.items():
        repository = init_repository(folder, get_repository_link(package), branch)
        try:
            checkout(repository, package, branch)
        except MissingBranchError:
            if from_branch:
                try:
                    if push_missing_branches:
                        create_branch_from_remote(
                            repository,
                            package,
                            branch,
                            from_branch,
                            True
                        )
                    else:
                        try:
                            checkout(repository, package, from_branch)
                        except MissingBranchError:
                            packages_with_missing_base_branches.append(package)
                except MissingBaseBranchError:
                    packages_with_missing_base_branches.append(package)
                except RepositoryDirtyError:
                    packages_with_dirty_repositories.append(package)
                except Exception as e:
                    logging.error(e)
                    packages_with_missing_branches.append(package)
            else:
                packages_with_missing_branches.append(package)
        except RepositoryDirtyError:
            packages_with_dirty_repositories.append(package)
        except Exception as e:
            logging.error(e)

    if 0 < len(packages_with_missing_branches):
        print(f'The following packages do not have the {branch} branch: {packages_with_missing_branches}')
    if 0 < len(packages_with_missing_base_branches):
        print(f'The following packages do not have the fallback {from_branch} branch: {packages_with_missing_base_branches}')
    if 0 < len(packages_with_dirty_repositories):
        print(f'The following packages have local changes and were not switched to {branch}: {packages_with_dirty_repositories}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to manage git multi-repositories.')
    parser.add_argument('--config', '-c', required=True, help='Path to the config json file')
    parser.add_argument('--from-branch', type=str, help='Fallback remote branch to create the target branch from if it does not exist')
    parser.add_argument('--push-missing-branches', action='store_true', help='Push newly created missing branches to origin')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug logging')
    app_args = parser.parse_args()

    if app_args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    config_file_path = os.path.abspath(app_args.config)
    working_dir = os.path.dirname(config_file_path)
    os.chdir(working_dir)

    main(
        get_current_git_branch(),
        config_file_path,
        app_args.from_branch,
        app_args.push_missing_branches
    )
