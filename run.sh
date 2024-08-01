#!/bin/bash

set -e

# this mkes the directory equal to where the script is located
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)"

function install {
    python -m pip install --upgrade pip
    python -m pip install --editable "$THIS_DIR/[dev]"
}

function lint {
    pre-commit run --all-files
}

function build {
    python -m build --sdist --wheel "$THIS_DIR/"
}

function try-load-dotenv {
    [ -f "${THIS_DIR}/.env" ] || (echo "no .env file found" && return 1)
    while IFS='=' read -r key value; do
        # Ignore empty lines and lines starting with #
        if [[ -n "$key" && "$key" != \#* ]]; then
            export "$key=$value"
        fi
    done < <(grep -v '^#' "$THIS_DIR/.env" | grep -v '^$')
}

function lint:ci {
    SKIP=no-commit-to-branch pre-commit run --all-files
}

function release:test {
    lint
    clean
    build
    publish:test
}

function release:prod {
    release:test
    publish:prod
}

function publish:test {
    try-load-dotenv || true
    twine upload dist/* \
    --repository testpypi \
    --username=__token__ \
    --password="$TEST_PYPI_TOKEN"
}

function publish:prod {
    try-load-dotenv || true
    twine upload dist/* \
    --repository pypi \
    --username=__token__ \
    --password="$PROD_PYPI_TOKEN"
}

function clean {
    rm -rf dist build
    find . \
       -type d \
       \( \
       -name "*cache*" \
       -o -name "*.dist-info" \
       -o -name "*.egg-info" \
       \) \
       -not -path "./venv/*" \
       -not -path "./.venv/*" \
       -not -path "./.env/*" \
       -not -path "./env/*" \
       -exec rm -r {} +
}

function start {
    echo "start not implemented"
}

function test {
    echo "test not implement"
}

function default {
    # Default task to execute
    start
}

function help {
    echo "$0 <task> <args>"
    echo "Tasks:"
    compgen -A function | cat -n
}

TIMEFORMAT="Task completed in %3lR"
time ${@:-help}
