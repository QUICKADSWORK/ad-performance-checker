#!/bin/bash
cd "$(dirname "$0")"
if [ ! -d "venv" ]; then
  echo "Creating venv and installing dependencies..."
  python3 -m venv venv
  ./venv/bin/pip install -r requirements.txt
fi
./venv/bin/python main.py
