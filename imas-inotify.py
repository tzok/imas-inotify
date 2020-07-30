#! /usr/bin/env python
import argparse
import os
import pwd
import re
from typing import Tuple

import pyinotify

MASKNAME = 'IN_CLOSE_WRITE'
MASK = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS'][MASKNAME]


class EventHandler:
    def __init__(self, user: str, tokamak: str, version: str):
        self.__files = set()
        self.__user = user
        self.__tokamak = tokamak
        self.__version = version

    def handle_event(self, event: pyinotify.Event):
        if event.maskname == MASKNAME:
            self.__files.add(event.pathname)
            core, _ = os.path.splitext(event.pathname)

            components = [f'{core}{extension}' for extension in ('.characteristics', '.datafile', '.tree')]
            if all(component in self.__files for component in components):
                shot, run = self.parse_shot_run(core)
                print(f'Data ready for user={self.__user} tokamak={self.__tokamak} version={self.__version} '
                      f'shot={shot} run={run}')
                for component in components:
                    self.__files.remove(component)

    def parse_shot_run(self, core: str) -> Tuple[int, int]:
        number = os.path.basename(core).replace('ids_', '')
        shot = int(number[:-4].lstrip('0'))  # last 4 digits are for run
        run = os.path.basename(os.path.dirname(core)) + number[-4:]
        run = int(run.lstrip('0'))
        return shot, run


def get_passwd(name: str = None) -> pwd.struct_passwd:
    return pwd.getpwnam(name) if name else pwd.getpwuid(os.getuid())


def generate_path(name: str, tokamak: str, version: str) -> str:
    return os.path.join(get_passwd(name).pw_dir, 'public', 'imasdb', tokamak, version)


def parse_path(path: str) -> Tuple[str, str, str]:
    match = re.search(r'.+/(.+?)/public/imasdb/(.+?)/([^/]+).*', os.path.abspath(path))
    if match:
        return match.group(1), match.group(2), match.group(3)
    else:
        return '', '', ''


if __name__ == '__main__':
    user = get_passwd().pw_name
    tokamak = 'test'
    version = '3'
    path = generate_path(user, tokamak, version)

    parser = argparse.ArgumentParser(description='Watch for creation of pulsefiles')
    parser.add_argument('--user', '-u', help=f'username whose imasdb is about to be watched [default={user}]')
    parser.add_argument('--tokamak', '-t', help=f'tokamak name [default={tokamak}]')
    parser.add_argument('--version', '-v', help=f'version [default={version}]')
    parser.add_argument('--path', '-p', help=f'full path where to look for pulsefiles '
                                             f'(this switch overrides --user, --tokamak and --version) [default={path}]')
    args = parser.parse_args()

    if args.path:
        path = args.path
        user, tokamak, version = parse_path(path)
    elif args.user or args.tokamak or args.version:
        user = args.user if args.user else user
        tokamak = args.tokamak if args.tokamak else tokamak
        version = args.version if args.version else version
        path = generate_path(user, tokamak, version)

    print(f'Establishing watches for {path}')

    handler = EventHandler(user, tokamak, version)

    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm)
    wm.add_watch(path, MASK, proc_fun=handler.handle_event, rec=True, auto_add=True)
    notifier.loop()
