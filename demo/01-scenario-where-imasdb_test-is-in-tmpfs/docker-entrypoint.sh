#! /bin/bash
sudo chown -R imas:imas /home/imas/public/imasdb/test
imasdb test > /dev/null
exec "$@"
