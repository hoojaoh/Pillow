#!/bin/bash

# gather the coverage data
if [[ "$MATRIX_OS" == "macOS-latest" ]]; then
    brew install lcov
else
    sudo apt-get -qq install lcov
fi

lcov --capture --directory . -b . --output-file coverage.info
#  filter to remove system headers
lcov --remove coverage.info '/usr/*' -o coverage.filtered.info
#  convert to json
gem install coveralls-lcov
coveralls-lcov -v -n coverage.filtered.info > coverage.c.json

coverage report
pip install codecov
pip install coveralls-merge
coveralls-merge coverage.c.json
codecov

if [ "$TRAVIS_PYTHON_VERSION" == "3.7" ] && [ "$DOCKER" == "" ]; then
    # Coverage and quality reports on just the latest diff.
    depends/diffcover-install.sh
    depends/diffcover-run.sh
fi
