#!/bin/bash
set -ex

SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
cd ${SCRIPT_PATH}
mkdir -p build
cmake -B build . -GNinja
cd build
ninja
exec ./run-test
