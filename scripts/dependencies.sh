#!/bin/bash

set -euo pipefail

if ! [ -x "$(command -v poetry)" ]; then
  if ! [ -x "$(command -v pipx)" ]; then
    python -m pip install --user pipx --isolated
    python -m pipx ensurepath
  fi
  pipx install poetry
fi
