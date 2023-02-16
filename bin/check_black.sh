#!/bin/sh

SCRIPT_DIR=$(dirname "$0")
black . "${SCRIPT_DIR}/.." --check
