#!/bin/bash

EXIT_STATUS=0

black --config .black.toml . || ((EXIT_STATUS++))
pylint --rcfile .pylintrc app/. || ((EXIT_STATUS++))

exit $EXIT_STATUS