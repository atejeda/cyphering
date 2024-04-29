#!/usr/bin/env bash

BASEDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
INSTALL=$BASEDIR/../../deps

mkdir -p $INSTALL

git clone --recursive https://github.com/jinja2cpp/Jinja2Cpp.git src
cp -rf nonstd src/thirdparty/
cd src
git submodule -q update --init

mkdir -p .build
cd .build
cmake .. -DCMAKE_INSTALL_PREFIX=$INSTALL -DJINJA2CPP_DEPS_MODE=internal
cmake --build . --target install