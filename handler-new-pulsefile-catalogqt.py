#! /usr/bin/env python
import argparse
import json
import logging
import os
import subprocess

from typing import Tuple


def parse_path(core: str) -> Tuple[str, str, str, int, int]:
    '''
    Parse path and filename to retrieve user, machine, version, shot and run.

    :param core: The path to file without extension i.e. /home/imas/public/imasdb/test/3/0/ids_10001
    :return: A 5-tuple with user, machine, version, shot and run.
    '''
    core, basename = os.path.split(core)  # /home/imas/public/imasdb/test/3/0 ids_10001
    core, run_mult = os.path.split(core)  # /home/imas/public/imasdb/test/3 0
    core, version = os.path.split(core)  # /home/imas/public/imasdb/test 3
    core, tokamak = os.path.split(core)  # /home/imas/public/imasdb test
    core, _ = os.path.split(core)  # /home/imas/public imasdb
    user, _ = os.path.split(core)  # /home/imas public
    user = os.path.basename(user)

    if user in ('', 'mnt'):
        user = 'imas'

    number = basename.replace('ids_', '')
    shot = int(number[:-4].lstrip('0'))  # last 4 digits are for run
    run = run_mult + number[-4:]
    run = run.lstrip('0')
    run = int(run) if run else 0
    return user, tokamak, version, shot, run


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Watch for creation of pulsefiles')
    parser.add_argument('--jar', help='path to catalog-ws-client JAR',
                        default='/catalog_qt_2/client/catalog-ws-client/target/catalogAPI.jar')
    parser.add_argument('--url', help='URL of webservice endpoint', default='http://server:8080')
    parser.add_argument('file')
    args = parser.parse_args()

    core, extension = os.path.splitext(args.file)

    # process data only if the extension is .populate
    if extension == '.populate':
        user, tokamak, version, shot, run = parse_path(core)
        logging.info(
            f'Inferred settings from {args.file} filer: '
            f'user={user} tokamak={tokamak} version={version} shot={shot} run={run}')

        # try to parse contents of .populate file as JSON data
        try:
            with open(args.file) as infile:
                content = infile.read()
                data = json.loads(content if content.strip() else '{}')
            logging.debug(f'Loaded content of {args.file} file:\n{json.dumps(data, indent=4, sort_keys=True)}')
        except:
            data = dict()
            logging.warning(f'Failed to load the content of {args.file} file as JSON data')

        # add additional experiment URI params read from .populate JSON here
        if 'occurrence' in data:
            occurrence = f';occurrence={data["occurrence"]}'
            logging.info(f'Found occurrence setting: {data["occurrence"]}')
        else:
            occurrence = ''
            logging.info('Did not find occurrence setting, using default value')

        command = ['java',
                   '-jar',
                   args.jar,
                   '--run-as-service',
                   '-addRequest',
                   '--user',
                   'imas-inotify-auto-updater',
                   '--url',
                   args.url,
                   '--experiment-uri',
                   f'mdsplus:/?user={user};machine={tokamak};version={version};shot={shot};run={run}{occurrence}']
        logging.info(f'Executing command: {" ".join(command)}')
        subprocess.run(command)
