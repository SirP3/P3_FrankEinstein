# Local Python Environment

Use a local virtual environment. Do not install project dependencies into Homebrew/system Python.

Setup:

```bash
scripts/setup_local_env.sh
source .venv/bin/activate
python apps/youtube_mining/scripts/start_ui.py
```

The `.venv/` folder is local-only and must not be committed.
