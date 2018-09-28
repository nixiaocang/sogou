#!/bin/bash
# author jiaoguofu

CURDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$CURDIR/../src
export CONF=$CURDIR/../conf
export SRC=$CURDIR/../src
python3 -W ignore $CURDIR/../test/sogou_api_test.py

