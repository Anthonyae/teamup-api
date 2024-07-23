#!/bin/bash

set -e

black --config .black.toml .
pylint --rcfile .pylintrc .