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
    def __init__(self):
        self.__files = set()

    def generate_handler(self, realpath: str, abspath: str):
        def handle_event(self, event: pyinotify.Event):
            if event.maskname == MASKNAME:
                self.__files.add(event.pathname)
                core, _ = os.path.splitext(event.pathname)

                components = [f'{core}{extension}' for extension in
                              ('.characteristics', '.datafile', '.tree', '.populate')]
                if all(component in self.__files for component in components):
                    user, tokamak, version, shot, run = self.parse_path(core.replace(realpath, abspath))
                    print(f'Data ready for user={user} tokamak={tokamak} version={version} shot={shot} run={run}')
                    for component in components:
                        self.__files.remove(component)

        return handle_event

    def parse_path(self, core: str) -> Tuple[str, str, str, int, int]:
        match = re.search(r'.+/(.+?)/public/imasdb/(.+?)/([^/]+).*', core)
        user, tokamak, version = match.group(1), match.group(2), match.group(3)
        number = os.path.basename(core).replace('ids_', '')
        shot = int(number[:-4].lstrip('0'))  # last 4 digits are for run
        run = os.path.basename(os.path.dirname(core)) + number[-4:]
        run = int(run.lstrip('0'))
        return user, tokamak, version, shot, run


def get_passwd(name: str = None) -> pwd.struct_passwd:
    return pwd.getpwnam(name) if name else pwd.getpwuid(os.getuid())


def generate_path(name: str) -> str:
    return os.path.join(get_passwd(name).pw_dir, 'public', 'imasdb')


if __name__ == '__main__':
    user = get_passwd().pw_name
    path = generate_path(user)

    parser = argparse.ArgumentParser(description='Watch for creation of pulsefiles')
    parser.add_argument('--path', '-p', help=f'full path where to look for pulsefiles recursively [default={path}]',
                        default=path)
    args = parser.parse_args()

    print(f'Establishing watches for {path}')

    handler = EventHandler()
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm)
    wm.add_watch(path, MASK, proc_fun=handler.generate_handler(path, path), rec=True, auto_add=True)
    for subdir in os.listdir(path):
        subdir = os.path.join(path, subdir)
        if os.path.islink(subdir):
            realpath = os.path.realpath(subdir)
            abspath = os.path.abspath(subdir)
            wm.add_watch(subdir, MASK, proc_fun=handler.generate_handler(realpath, abspath), rec=True, auto_add=True)
    notifier.loop()
