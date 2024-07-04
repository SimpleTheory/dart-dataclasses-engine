import subprocess
import json
import sys
import http.client


module = 'dart-dataclasses-engine'
index_to_check = 'https://test.pypi.org/simple/'
internet_err_msg = 'It seems like I can\'t access the internet at the moment (シ_ _)シ\nPlease check your connection and try again. (、._. )、'
up_to_date_msg = 'It seems like you have the latest version ﾟヽ(｡◕‿◕｡)ﾉﾟ (≧∇≦).'

class Package:
    def __init__(self, name: str, outdated_ver: str, latest_ver: str):
        self.name = name
        self.outdated_ver = outdated_ver
        self.latest_ver = latest_ver

    def __str__(self):
        return f'{self.name} {self.outdated_ver} (new: {self.latest_ver})'

    def __repr__(self):
        return self.__str__()

def check_internet_connection():
    conn = http.client.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        response = conn.getresponse()
        return True if response.status == 200 else False
    except Exception:
        return False
    finally:
        conn.close()

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
    return f'\nThe package {pkg.name} is out of date!\n' \
           f'Your version is: {pkg.outdated_ver}\n' \
           f'But the newest version is: {pkg.latest_ver}\n' \
           f'To upgrade enter this command in the CMD:\n\n' \
           f'pip install --upgrade {index}{pkg.name}'

def check_msg_to_see_if_pkg_was_outdated(msg):
    return 'To upgrade enter this command in the CMD:' in msg

def update_precheck():
    msg = run()
    if check_msg_to_see_if_pkg_was_outdated(msg):
        print(msg)
        print()
        answer = input('There is a new version available, would you still like to run anyway? (y/N)').lower()
        if answer != 'y':
            sys.exit(0)


def run() -> str:
    if 'index_to_check' not in globals():
        index = None
    else:
        index = index_to_check
    if not check_internet_connection():
        return internet_err_msg
    outdated = get_outdated_packages(index_url=index)
    this = this_is_in_outdated_packages(outdated)
    if this:
        return message(this, index)
    else:
        return up_to_date_msg


def entry_main():
    print(run())


if __name__ == '__main__':
    entry_main()
