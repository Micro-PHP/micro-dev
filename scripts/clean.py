#!/usr/bin/env python3

import argparse
import logging
import os
import shutil

from packages import read_packages

logging.basicConfig(level=logging.INFO)


def remove_git_metadata(package_directory: str) -> bool:
    git_path = os.path.join(package_directory, '.git')

    if os.path.isdir(git_path) and not os.path.islink(git_path):
        shutil.rmtree(git_path)
        logging.info(f'Removed git directory from {package_directory}')
        return True

    if os.path.exists(git_path):
        os.remove(git_path)
        logging.info(f'Removed git file from {package_directory}')
        return True

    logging.info(f'No git metadata found in {package_directory}')
    return False


def main(config_file: str) -> list[str]:
    if not config_file:
        raise ValueError('No config file specified.')

    packages = read_packages(config_file)
    cleaned_packages = []

    for _, folder in packages.items():
        if remove_git_metadata(folder):
            cleaned_packages.append(folder)

    return cleaned_packages


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove git metadata created during multi-repository initialization.')
    parser.add_argument('--config', '-c', required=True, help='Path to the config json file')
    app_args = parser.parse_args()

    config_file_path = os.path.abspath(app_args.config)
    working_dir = os.path.dirname(config_file_path)
    os.chdir(working_dir)

    main(config_file_path)
