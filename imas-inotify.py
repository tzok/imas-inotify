#! /usr/bin/env python
import argparse
import configparser
import glob
import logging
import os
import subprocess
import sys

import pyinotify


class EventHandler:
    def generate_handler(self, realpath: str, abspath: str, mask: int, action: str, relative: bool, arguments: list):
        def handle_event(event: pyinotify.Event):
            logging.debug(f'Received inotify event: {event}')
            if event.mask & mask:
                path = event.pathname.replace(realpath, abspath)
                cwd = os.path.dirname(os.path.realpath(__file__)) if relative else None
                arguments_flat = ' '.join(arguments)
                logging.debug(f'Running {action} {arguments_flat} {path}' + (f' in working directory {cwd}' if cwd else ''))
                subprocess.run([action] + arguments + [path], cwd=cwd)

        return handle_event


def convert_to_arguments(additional: dict):
    for k, v in additional.items():
        yield '--{}'.format(k)
        yield v


if __name__ == '__main__':
    config = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.ini'))

    parser = argparse.ArgumentParser(description='Watch for creation of pulsefiles')
    parser.add_argument('--config', '-c', help=f'configuration file [default={config}]', default=config)
    parser.add_argument('--verbose', '-v', help=f'enable verbose output', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if not os.path.exists(config):
        logging.error(f'File does not exist: {args.config}')
        sys.exit()

    handler = EventHandler()
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm)

    ini = configparser.ConfigParser()
    ini.read(args.config)

    required = {'mask', 'glob', 'recursive', 'action', 'action_relative'}

    for section in ini.sections():
        if all(name in ini[section] for name in required):
            mask = 0
            for partial in ini[section]['mask'].split():
                mask |= pyinotify.EventsCodes.FLAG_COLLECTIONS['OP_FLAGS'][partial]
            pattern = os.path.expanduser(os.path.expandvars(ini[section]['glob']))
            recursive = bool(ini[section]['recursive'])
            action = ini[section]['action']
            action_relative = bool(ini[section]['action_relative'])
            arguments = list(convert_to_arguments({key: ini[section][key] for key in ini[section].keys() - required}))

            for path in glob.iglob(pattern):
                wm.add_watch(path, mask,
                             proc_fun=handler.generate_handler(path, path, mask, action, action_relative, arguments),
                             rec=recursive, auto_add=True)
                arguments_flat = ' '.join(arguments)
                logging.info(f'Establishing watches for {path} with action {action} {arguments_flat}')

                for subdir in os.listdir(path):
                    subdir = os.path.join(path, subdir)
                    if os.path.islink(subdir):
                        realpath = os.path.realpath(subdir)
                        abspath = os.path.abspath(subdir)
                        wm.add_watch(realpath, mask,
                                     proc_fun=handler.generate_handler(realpath, abspath, mask, action,
                                                                       action_relative),
                                     rec=recursive, auto_add=True)
                        logging.info(f'Establishing watches for {realpath} -> {abspath} with action {action}')

    notifier.loop()
