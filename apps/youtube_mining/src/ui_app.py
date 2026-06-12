#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

try:
    import streamlit as st
except Exception:
    print("Streamlit is not installed. Install it in the local environment before running the UI.")
    raise

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"

def run_command(args):
    result = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.stdout.strip()

def list_runs():
    if not OUTPUT_ROOT.exists():
        return []
    return sorted([p.name for p in OUTPUT_ROOT.iterdir() if p.is_dir()])

st.set_page_config(page_title="P3FE YTM v0.2", layout="wide")

st.title("P3FE YouTube Mining v0.2")
st.caption("Safety-first local source adapter shell")

st.warning("Skeleton UI only. No transcript mining is implemented here yet.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Runtime boundary")
    st.code(str(OUTPUT_ROOT))
    st.write("Runtime output is local-only and ignored by git.")

with col2:
    st.subheader("Safety status")
    if "safety_audit_output" not in st.session_state:
        st.session_state.safety_audit_output = ""

    if st.button("Run safety audit"):
        st.session_state.safety_audit_output = run_command(["python3", "scripts/safety/public_safety_audit.py"])

    if st.session_state.safety_audit_output:
        st.code(st.session_state.safety_audit_output)

st.subheader("Local YTM runs")

runs = list_runs()
if runs:
    st.write("Run count:", len(runs))
    for run in runs:
        st.write("-", run)
else:
    st.write("No local runs found.")

st.subheader("Create local run folder")

run_id = st.text_input("Run ID", value="ui-smoke-test-001")

if "create_run_output" not in st.session_state:
    st.session_state.create_run_output = ""

if st.button("Create run folder"):
    st.session_state.create_run_output = run_command(["python3", "apps/youtube_mining/scripts/create_run_folder.py", run_id])
    st.rerun()

if st.session_state.create_run_output:
    st.code(st.session_state.create_run_output)

st.subheader("Workspace dashboard")

if st.button("Run workspace dashboard"):
    st.code(run_command(["python3", "scripts/status_dashboard.py"]))

st.subheader("Current limitations")

st.markdown("""
- No YouTube download yet
- No transcript processing yet
- No local model call yet
- No radar-card generation yet
- No handoff generation yet
""")
