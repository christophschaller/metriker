#!/bin/sh

SCRIPT_DIR=$(dirname "$0")
pylint --recursive=y "${SCRIPT_DIR}/.."
