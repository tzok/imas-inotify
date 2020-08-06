#! /bin/bash
for tokamak in /mnt/imasdb/*; do
    [[ "${tokamak}" == "/mnt/imasdb/test" ]] && continue
    ln -s "${tokamak}" /home/imas/public/imasdb/
done
