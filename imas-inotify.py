#! /usr/bin/env python
import argparse
import configparser
import glob
import os
import subprocess
import sys

import pyinotify

CLOSE_WRITE = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_CLOSE_WRITE']
CLOSE_NOWRITE = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS']['IN_CLOSE_NOWRITE']
MASK = CLOSE_WRITE | CLOSE_NOWRITE


class EventHandler:
    def generate_handler(self, realpath: str, abspath: str, action: str, relative: bool):
        def handle_event(event: pyinotify.Event):
            if event.mask & MASK:
                path = event.pathname.replace(realpath, abspath)
                cwd = os.path.dirname(os.path.realpath(__file__)) if relative else None
                print(f'Running {action} {path}' + (f' in working directory {cwd}' if cwd else ''))
                subprocess.run([action, path], cwd=cwd)

        return handle_event


if __name__ == '__main__':
    config = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.ini'))

    parser = argparse.ArgumentParser(description='Watch for creation of pulsefiles')
    parser.add_argument('--config', '-c', help=f'configuration file [default={config}]', default=config)
    parser.add_argument('--dry-run', '-d', help='do not watch for files, just print out what would happen',
                        action='store_true')
    args = parser.parse_args()

    if not os.path.exists(config):
        print(f'File does not exist: {args.config}', file=sys.stderr)
        sys.exit()

    handler = EventHandler()
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm)

    ini = configparser.ConfigParser()
    ini.read(args.config)

    for section in ini.sections():
        if 'glob' in ini[section] and 'action' in ini[section]:
            pattern = os.path.expanduser(os.path.expandvars(ini[section]['glob']))
            action = ini[section]['action']
            relative = bool(ini[section]['relative']) if 'relative' in ini[section] else False

            for path in glob.iglob(pattern):
                wm.add_watch(path, MASK, proc_fun=handler.generate_handler(path, path, action, relative), rec=True,
                             auto_add=True)
                print(f'Establishing watches for {path} with action {action}')

                for subdir in os.listdir(path):
                    subdir = os.path.join(path, subdir)
                    if os.path.islink(subdir):
                        realpath = os.path.realpath(subdir)
                        abspath = os.path.abspath(subdir)
                        wm.add_watch(realpath, MASK,
                                     proc_fun=handler.generate_handler(realpath, abspath, action, relative), rec=True,
                                     auto_add=True)
                        print(f'Establishing watches for {realpath} -> {abspath} with action {action}')

    notifier.loop()
