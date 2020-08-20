#! /usr/bin/env python
import json
import logging
import os
import re
import subprocess
import sys
from typing import Tuple


def parse_path(core: str) -> Tuple[str, str, str, int, int]:
    '''
    Parse path and filename to retrieve user, machine, version, shot and run.

    :param core: The path to file without extension i.e. /home/imas/public/imasdb/test/3/0/ids_10001
    :return: A 5-tuple with user, machine, version, shot and run.
    '''
    match = re.search(r'.+/(.+?)/public/imasdb/(.+?)/([^/]+).*', core)
    user, tokamak, version = match.group(1), match.group(2), match.group(3)
    number = os.path.basename(core).replace('ids_', '')
    shot = int(number[:-4].lstrip('0'))  # last 4 digits are for run
    run = os.path.basename(os.path.dirname(core)) + number[-4:]
    run = run.lstrip('0')
    run = int(run) if run else 0
    return user, tokamak, version, shot, run


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) == 2:
        core, extension = os.path.splitext(sys.argv[1])

        # process data only if the extension is .populate
        if extension == '.populate':
            user, tokamak, version, shot, run = parse_path(core)
            logging.info(
                f'Inferred settings from {sys.argv[1]} filer: '
                f'user={user} tokamak={tokamak} version={version} shot={shot} run={run}')

            # try to parse contents of .populate file as JSON data
            try:
                with open(sys.argv[1]) as infile:
                    content = infile.read()
                    data = json.loads(content if content.strip() else '{}')
                logging.debug(f'Loaded content of {sys.argv[1]} file:\n{json.dumps(data, indent=4, sort_keys=True)}')
            except:
                data = dict()
                logging.warning(f'Failed to load the content of {sys.argv[1]} file as JSON data')

            # add additional experiment URI params read from .populate JSON here
            if 'occurrence' in data:
                occurrence = f';occurrence={data["occurrence"]}'
                logging.info(f'Found occurrence setting: {data["occurrence"]}')
            else:
                occurrence = ''
                logging.info('Did not find occurrence setting, using default value')

            command = ['java',
                       '-jar',
                       '/home/imas/opt/catalog_qt_2/client/catalog-ws-client/target/catalogAPI.jar',
                       '-addRequest',
                       '--user',
                       'imas-inotify-auto-updater',
                       '--url',
                       'http://localhost:8080',
                       '--experiment-uri',
                       f'mdsplus:/?user={user};machine={tokamak};version={version};shot={shot};run={run}{occurrence}']
            logging.info(f'Executing command: {" ".join(command)}')
            subprocess.run(command)
