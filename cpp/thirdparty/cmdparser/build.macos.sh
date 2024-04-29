#!/usr/bin/env bash

BASEDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
INSTALL=$BASEDIR/../../deps

mkdir -p $INSTALL

git clone git@github.com:FlorianRappl/CmdParser.git src
cd src

# mkdir -p .build
# cd .build
# cmake .. -DCMAKE_INSTALL_PREFIX=$INSTALL -DJINJA2CPP_DEPS_MODE=internal
# cmake --build . --target install