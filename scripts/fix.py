#!/usr/bin/env python3

import os, logging, argparse

from git import InvalidGitRepositoryError

from packages import read_packages
from packagist import get_repository_link
from git_commands import get_repository, update_repository_remote_link

logging.basicConfig(level=logging.INFO)

def main(config_file):
    if not config_file:
        raise ValueError('No config file specified.')

    packages = read_packages(config_file)

    failed_packages = []
    for package, folder in packages.items():
        logging.info(f"Processing package {package} in folder {folder}")
        original_directory = os.getcwd()
        os.chdir(folder)
        try:
            repo = get_repository('.')
            update_repository_remote_link(repo, 'origin', get_repository_link(package))
        except InvalidGitRepositoryError:
            logging.error(f"Invalid git repository {folder}")
            failed_packages.append(package)
        except Exception as e:
            logging.error(e)
            failed_packages.append(package)
        finally:
            os.chdir(original_directory)

    if 0 < len(failed_packages):
        logging.error(f'The following packages has not been updated and should be processed manually: {failed_packages}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to manage git multi-repositories.')
    parser.add_argument('--config', '-c', required=True, help='Path to the config json file')
    app_args = parser.parse_args()

    main(app_args.config)
