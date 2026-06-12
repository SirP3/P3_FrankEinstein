#!/bin/zsh
cd "$(dirname "$0")/../.."
source .venv/bin/activate
python apps/youtube_mining/scripts/start_ui.py
