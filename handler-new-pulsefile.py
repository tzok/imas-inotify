#! /usr/bin/env python
import os
import re
import sys
from typing import Tuple


def parse_path(core: str) -> Tuple[str, str, str, int, int]:
    match = re.search(r'.+/(.+?)/public/imasdb/(.+?)/([^/]+).*', core)
    user, tokamak, version = match.group(1), match.group(2), match.group(3)
    number = os.path.basename(core).replace('ids_', '')
    shot = int(number[:-4].lstrip('0'))  # last 4 digits are for run
    run = os.path.basename(os.path.dirname(core)) + number[-4:]
    run = int(run.lstrip('0'))
    return user, tokamak, version, shot, run


if __name__ == '__main__':
    if len(sys.argv) == 2:
        core, extension = os.path.splitext(sys.argv[1])
        if extension == '.populate':
            user, tokamak, version, shot, run = parse_path(core)
            print(f'Data ready for user={user} tokamak={tokamak} version={version} shot={shot} run={run}')
