#!/usr/bin/python3
import argparse
import pip

from pip.commands.list import ListCommand, format_for_columns, tabulate
from pip.utils import get_installed_distributions


def convert_to_bool(argument):
    lowered = argument.lower()
    if lowered in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
        return True
    elif lowered in ('no', 'n', 'false', 'f', '0', 'disable', 'off'):
        return False
    else:
        raise ValueError(lowered + ' is not a recognised boolean option')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--show-upgradeable', action='store_true', default=False)
    parser.add_argument('--yes', '-y', action='store_true', default=False)
    parser.add_argument('--filter', nargs='+')
    return parser.parse_args()


def print_distributions(packages, opts):
    data, header = format_for_columns(packages, opts)
    data.insert(0, header)
    pkg_str, sizes = tabulate(data)
    pkg_str.insert(1, " ".join(map(lambda x: '-' * x, sizes)))
    pkg_str.append(f'\nThere are {len(packages)} packages to be upgraded.' if len(packages) > 1 else '\nThere is one package to be upgraded.')
    print('\n'.join(pkg_str))


if __name__ == '__main__':
    main_opts = parse_args()
    list_cmd = ListCommand()
    list_opts = list_cmd.parse_args(['--outdated'])[0]
    distributions = [d for d in list_cmd.iter_packages_latest_infos(get_installed_distributions(), list_opts) if d.latest_version > d.parsed_version]
    distributions = sorted(distributions, key=lambda p: p.project_name.lower())
    if not distributions:
        print('There are no packages to be upgraded.')
        exit(0)
    print_distributions(distributions, list_opts)
    if main_opts.show_upgradeable:
        exit(0)
    if main_opts.filter:
        filters = [string.lower() for string in main_opts.filter]
        excluded = []
        for package in distributions:
            if package.project_name.lower() in filters:
                excluded.append(distributions.pop(distributions.index(package)).project_name)
        if len(excluded) == 0:
            print('WARNING: Your filter didn\'t removed any packages from upgrading. You might wanna check that before upgrading.')
        else:
            print(f'The following packages won\'t be installed: {", ".join(excluded)}' if len(excluded) > 1 else f'The package {excluded[0]} won\'t be upgraded.')
    if main_opts.yes or convert_to_bool(input('Do you want to continue? [y/n]: ')):
        print('\n')
        pip.main(['install', '--upgrade'] + [p.project_name for p in distributions])
    else:
        exit(0)
