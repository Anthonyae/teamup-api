#!/bin/bash

black --config .black.toml .
pylint --rcfile .pylintrc app/.