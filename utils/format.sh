#!/bin/bash

set -e

cd "$(dirname "$0")"/..

clang-format -i src/*