from pathlib import Path
import re
import subprocess

try:
    import streamlit as st
except Exception:
    print("Streamlit is not installed. Run scripts/setup_local_env.sh first.")
    raise

ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = ROOT / "output" / "youtube_mining"
ALLOWED_SOURCE_EXTENSIONS = {".md", ".txt", ".vtt", ".srt", ".json"}

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

def safe_run_id(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "run"

def list_runs():
    if not OUTPUT_ROOT.exists():
        return []
    return sorted([p.name for p in OUTPUT_ROOT.iterdir() if p.is_dir()])

def source_files(run_id: str):
    source_dir = OUTPUT_ROOT / run_id / "source"
    if not source_dir.exists():
        return []
    return sorted([
        p for p in source_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in ALLOWED_SOURCE_EXTENSIONS
    ])

def write_uploaded_source(run_id: str, uploaded_file) -> Path:
    run_id = safe_run_id(run_id)
    name = Path(uploaded_file.name).name
    suffix = Path(name).suffix.lower()
    if suffix not in ALLOWED_SOURCE_EXTENSIONS:
        raise ValueError("Unsupported source extension: " + suffix)
    target_dir = OUTPUT_ROOT / run_id / "source"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / name
    target.write_bytes(uploaded_file.getbuffer())
    return target

for key in ["safety_audit_output", "create_run_output", "workspace_dashboard_output", "upload_output"]:
    if key not in st.session_state:
        st.session_state[key] = ""

st.set_page_config(page_title="P3FE YTM v0.2", layout="wide")

st.title("P3FE YouTube Mining v0.2")
st.caption("Safety-first local source adapter shell")
st.warning("Skeleton UI. Source intake exists. Transcript mining is not implemented yet.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Runtime boundary")
    st.code(str(OUTPUT_ROOT))
    st.write("Runtime output is local-only and ignored by git.")

with col2:
    st.subheader("Safety status")
    if st.button("Run safety audit"):
        st.session_state.safety_audit_output = run_command(["python3", "scripts/safety/public_safety_audit.py"])
    if st.session_state.safety_audit_output:
        st.code(st.session_state.safety_audit_output)

st.subheader("Local YTM runs")

runs = list_runs()
if runs:
    st.write("Run count:", len(runs))
    selected_run = st.selectbox("Selected run", runs, index=len(runs) - 1)
else:
    st.write("No local runs found.")
    selected_run = ""

if selected_run:
    st.subheader("Source status")
    files = source_files(selected_run)
    st.write("Selected run:", selected_run)
    st.write("Source file count:", len(files))
    if files:
        for file in files:
            st.write("-", file.relative_to(OUTPUT_ROOT / selected_run))
    else:
        st.write("No source files in this run yet.")

st.subheader("Create local run folder")
run_id = st.text_input("Run ID", value="ui-smoke-test-001")
if st.button("Create run folder"):
    st.session_state.create_run_output = run_command(["python3", "apps/youtube_mining/scripts/create_run_folder.py", run_id])
    st.rerun()
if st.session_state.create_run_output:
    st.code(st.session_state.create_run_output)

st.subheader("Manual source intake")
if selected_run:
    uploaded = st.file_uploader("Add one local-only source file to selected run", type=["md", "txt", "vtt", "srt", "json"])
    if uploaded is not None and st.button("Save uploaded source to selected run"):
        try:
            target = write_uploaded_source(selected_run, uploaded)
            st.session_state.upload_output = "SAVED " + str(target)
            st.rerun()
        except Exception as exc:
            st.session_state.upload_output = "ERROR " + str(exc)
if st.session_state.upload_output:
    st.code(st.session_state.upload_output)

st.subheader("Derived placeholder")
if selected_run:
    if st.button("Build derived placeholder"):
        st.session_state.derived_output = run_command(["python3", "apps/youtube_mining/scripts/build_derived_placeholder.py", selected_run])
    if "derived_output" in st.session_state and st.session_state.derived_output:
        st.code(st.session_state.derived_output)

st.subheader("Workspace dashboard")
if st.button("Run workspace dashboard"):
    st.session_state.workspace_dashboard_output = run_command(["python3", "scripts/status_dashboard.py"])
if st.session_state.workspace_dashboard_output:
    st.code(st.session_state.workspace_dashboard_output)

st.subheader("Current limitations")
st.markdown("- No YouTube download yet\n- No transcript processing yet\n- No local model call yet\n- No radar-card generation yet\n- No handoff generation yet")
