#!/usr/bin/env bash
# Install CPython 3.7 and create a venv. Usage: install_py37.sh <uv|micromamba|deadsnakes> <venv_dir>
# Runs as root inside an ubuntu:22.04 container (no sudo). Prints the Python and OpenSSL versions.
set -euo pipefail
method="$1"
venv="$2"
case "$method" in
  uv)
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    uv python install 3.7
    uv venv --seed --python 3.7 "$venv"
    ;;
  micromamba)
    curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj bin/micromamba
    ./bin/micromamba create -y -p "${venv}-conda" -c conda-forge python=3.7
    "${venv}-conda/bin/python" -m venv "$venv"
    ;;
  deadsnakes)
    apt-get install -y software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update
    apt-get install -y python3.7 python3.7-venv python3.7-dev
    python3.7 -m venv "$venv"
    ;;
  *)
    echo "unknown method: $method" >&2
    exit 2
    ;;
esac
"$venv/bin/python" --version
"$venv/bin/python" -c "import ssl, sqlite3, zlib, ctypes; print('openssl', ssl.OPENSSL_VERSION)"
