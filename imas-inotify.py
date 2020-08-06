#! /usr/bin/env python
import argparse
import configparser
import glob
import os
import subprocess
import sys

import pyinotify


class EventHandler:
    def generate_handler(self, realpath: str, abspath: str, action: str, relative: bool):
        def handle_event(event: pyinotify.Event):
            path = event.pathname.replace(realpath, abspath)
            cwd = os.path.dirname(os.path.realpath(__file__)) if relative else None
            print(f'Running {action} {path}' + (f' in working directory {cwd}' if cwd else ''))
            subprocess.run([action, path], cwd=cwd)

        return handle_event


if __name__ == '__main__':
    config = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.ini'))

    parser = argparse.ArgumentParser(description='Watch for creation of pulsefiles')
    parser.add_argument('--config', '-c', help=f'configuration file [default={config}]', default=config)
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
        if all(name in ini[section] for name in ('mask', 'glob', 'recursive', 'action', 'action_relative')):
            mask = pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS'][ini[section]['mask']]
            pattern = os.path.expanduser(os.path.expandvars(ini[section]['glob']))
            recursive = bool(ini[section]['recursive'])
            action = ini[section]['action']
            action_relative = bool(ini[section]['relative'])

            for path in glob.iglob(pattern):
                wm.add_watch(path, mask,
                             proc_fun=handler.generate_handler(path, path, action, action_relative),
                             rec=recursive, auto_add=True)
                print(f'Establishing watches for {path} with action {action}')

                for subdir in os.listdir(path):
                    subdir = os.path.join(path, subdir)
                    if os.path.islink(subdir):
                        realpath = os.path.realpath(subdir)
                        abspath = os.path.abspath(subdir)
                        wm.add_watch(realpath, mask,
                                     proc_fun=handler.generate_handler(realpath, abspath, action, action_relative),
                                     rec=recursive, auto_add=True)
                        print(f'Establishing watches for {realpath} -> {abspath} with action {action}')

    notifier.loop()
