#!/usr/bin/env python3

import os, logging, argparse

from packages import read_packages
from packagist import get_repository_link
from git_shell import get_current_git_branch
from git_commands import checkout, init_repository, MissingBranchError

logging.basicConfig(level=logging.INFO)

def main(branch, config_file):
    if not config_file:
        raise ValueError('No config file specified.')

    packages = read_packages(config_file)

    packages_with_missing_branches = []
    for package, folder in packages.items():
        repository = init_repository(folder, get_repository_link(package))
        try:
            checkout(repository, package, branch)
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

    main(get_current_git_branch(), config_file_path)
