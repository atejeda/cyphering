#!/usr/bin/env bash

BASEDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
INSTALL=$BASEDIR/../../deps

mkdir -p $INSTALL

git clone --recursive https://github.com/biojppm/rapidyaml.git src
cd src
git submodule -q update --init

mkdir -p .build
cd .build
cmake .. -DCMAKE_INSTALL_PREFIX=$INSTALL -DYAML_BUILD_SHARED_LIBS=ON
cmake --build . --target install 