#!/bin/bash

set -x
set -e

this_dir=$(dirname "$0")
pushd "${this_dir}/.." >/dev/null

# Clean previous coverage
rm -f .coverage htmlcov/* || true

python3 -m pip install pytest pytest-cov # coverage

# Generate dynamic file list
python3 -m pytest --cov --cov-report=term-missing --cov-report=html

popd >/dev/null