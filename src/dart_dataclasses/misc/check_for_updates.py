import subprocess
import json
import sys

module = 'dart-dataclasses-engine'
index_to_check = 'https://test.pypi.org/simple/'


class Package:
    def __init__(self, name: str, outdated_ver: str, latest_ver: str):
        self.name = name
        self.outdated_ver = outdated_ver
        self.latest_ver = latest_ver


def get_outdated_packages(index_url=None) -> list[Package]:
    if index_url:
        command = ['pip', 'list', '--outdated', '--format=json', '--index-url', index_url]
    else:
        command = ['pip', 'list', '--outdated', '--format=json']
    output = subprocess.check_output(command)
    outdated_packages = []
    for package in json.loads(output.decode()):
        outdated_packages.append(Package(package['name'], package['version'], package['latest_version']))
    return outdated_packages


def this_is_in_outdated_packages(outdated: list[Package]) -> Package | None:
    for package in outdated:
        if package.name == module:
            return package
    return None


def message(pkg: Package, index_url=None) -> str:
    index = ''
    if index_url:
        index = f'-i {index_url} '
    return f'The package {pkg.name} is out of date!\n' \
           f'The your version is: {pkg.outdated_ver}\n' \
           f'But the newest version is: {pkg.latest_ver}\n' \
           f'To upgrade enter this command in the CMD:\n\n' \
           f'pip install --upgrade {index}{pkg.name}'


def update_precheck():
    msg = run()
    if msg:
        print(msg)
        print()
        answer = input('There is a new version available, would you still like to run anyway? (y/N)').lower()
        if answer != 'y':
            sys.exit(0)


def run() -> str | None:
    if 'index_to_check' not in globals():
        index = None
    else:
        index = index_to_check
    outdated = get_outdated_packages(index_url=index)
    this = this_is_in_outdated_packages(outdated)
    if this:
        return message(this, index)
    else:
        return None


def entry_main():
    print(run())
