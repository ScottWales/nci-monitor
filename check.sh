#!/bin/bash

ERRS=0

ruff format .
ERRS+=$?

ruff check --fix .
ERRS+=$?

mypy .
ERRS+=$?

pytest .
ERRS+=$?

if [[ "$ERRS" -eq 0 ]]; then
    echo PASS
else
    echo FAIL "$ERRS"
fi
