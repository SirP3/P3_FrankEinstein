#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
APP = ROOT / "apps" / "youtube_mining" / "src" / "ui_app.py"

def main() -> int:
    if not APP.exists():
        print("YTM UI app not found:", APP)
        return 1

    cmd = [sys.executable, "-m", "streamlit", "run", str(APP)]
    print("Starting YTM UI:")
    print(" ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)

if __name__ == "__main__":
    raise SystemExit(main())
