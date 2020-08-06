#! /bin/bash
[[ ! -e "/home/imas/public/imasdb/$(basename $1)" ]] && ln -s "$1" /home/imas/public/imasdb/
