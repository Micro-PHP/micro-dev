#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    with path.open() as file:
        return json.load(file)


def collect_src_package_names(src_dir: Path) -> set[str]:
    package_names = set()

    for composer_file in src_dir.rglob('composer.json'):
        package_name = load_json(composer_file).get('name')
        if package_name:
            package_names.add(package_name)

    return package_names


def collect_dependencies(src_dir: Path, internal_packages: set[str], include_internal: bool) -> dict[str, dict[str, str]]:
    dependencies = {
        'require': {},
        'require-dev': {},
    }

    for composer_file in sorted(src_dir.rglob('composer.json')):
        package = load_json(composer_file)

        for section in dependencies:
            for name, constraint in package.get(section, {}).items():
                if not include_internal and name in internal_packages:
                    continue

                dependencies[section].setdefault(name, str(constraint))

    return dependencies


def merge_dependencies(root_composer: dict, dependencies: dict[str, dict[str, str]]) -> dict[str, list[str]]:
    changes = {
        'added': [],
        'kept': [],
        'conflicts': [],
    }

    for section, packages in dependencies.items():
        root_composer.setdefault(section, {})

        for name, constraint in sorted(packages.items()):
            current_constraint = root_composer[section].get(name)

            if current_constraint is None:
                root_composer[section][name] = constraint
                changes['added'].append(f'{section}: {name} {constraint}')
                continue

            if current_constraint == constraint:
                changes['kept'].append(f'{section}: {name} {constraint}')
                continue

            changes['conflicts'].append(
                f'{section}: {name} root has {current_constraint}, src has {constraint}'
            )

    return changes


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False) + '\n')


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Merge dependencies from src/**/composer.json files into the root composer.json.'
    )
    parser.add_argument('--root', default='composer.json', help='Path to the root composer.json file')
    parser.add_argument('--src', default='src', help='Path to the src directory')
    parser.add_argument('--include-internal', action='store_true', help='Also merge dependencies on packages found in src')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without writing composer.json')
    args = parser.parse_args()

    root_composer_file = Path(args.root)
    src_dir = Path(args.src)

    root_composer = load_json(root_composer_file)
    internal_packages = collect_src_package_names(src_dir)
    dependencies = collect_dependencies(src_dir, internal_packages, args.include_internal)
    changes = merge_dependencies(root_composer, dependencies)

    for change_type in ('added', 'conflicts'):
        for change in changes[change_type]:
            print(f'{change_type}: {change}')

    if not args.dry_run:
        write_json(root_composer_file, root_composer)


if __name__ == '__main__':
    main()
