#!/usr/bin/env python3

import argparse
import logging
import os
import shutil

from packages import read_packages

logging.basicConfig(level=logging.INFO)


def remove_path(path: str, dry_run: bool) -> bool:
    if not os.path.lexists(path):
        logging.info(f'Skipped missing path: {path}')
        return False

    if dry_run:
        logging.info(f'Would remove: {path}')
        return True

    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

    logging.info(f'Removed: {path}')
    return True


def clean_package(package: str, folder: str, dry_run: bool) -> list[str]:
    removed_paths = []

    for path in (
        os.path.join(folder, 'vendor'),
        os.path.join(folder, 'composer.lock'),
    ):
        if remove_path(path, dry_run):
            removed_paths.append(path)

    if not removed_paths:
        logging.info(f'No Composer artifacts found in {package}')

    return removed_paths


def main(config_file: str, dry_run: bool) -> dict[str, list[str]]:
    if not config_file:
        raise ValueError('No config file specified.')

    packages = read_packages(config_file)
    cleaned_packages = {}

    for package, folder in packages.items():
        removed_paths = clean_package(package, folder, dry_run)
        if removed_paths:
            cleaned_packages[package] = removed_paths

    return cleaned_packages


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove Composer artifacts from all configured package repositories.')
    parser.add_argument('--config', '-c', default='./repository.json', help='Path to the config json file')
    parser.add_argument('--dry-run', action='store_true', help='Print paths that would be removed without deleting them')
    app_args = parser.parse_args()

    config_file_path = os.path.abspath(app_args.config)
    working_dir = os.path.dirname(config_file_path)
    os.chdir(working_dir)

    main(config_file_path, app_args.dry_run)
