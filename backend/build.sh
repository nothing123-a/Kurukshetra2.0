#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip and install build tools
pip install --upgrade pip
pip install setuptools wheel

# Install requirements
pip install -r requirements.txt
