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

def operator_brief_path(run_id: str) -> Path:
    return OUTPUT_ROOT / run_id / "handoffs" / "operator_brief.md"

def pipeline_smoke_report_path(run_id: str) -> Path:
    return OUTPUT_ROOT / run_id / "handoffs" / "ytm_pipeline_smoke_report.md"

def run_summary_files(run_id: str) -> list[tuple[str, Path]]:
    run_dir = OUTPUT_ROOT / run_id
    relative_paths = [
        "derived/source_inventory.md",
        "derived/transcript_index.md",
        "derived/model_input_manifest.md",
        "derived/radar_cards/radar-card-validation-report.md",
        "handoffs/operator_brief.md",
        "handoffs/radar_card_brief.md",
        "handoffs/ytm_pipeline_smoke_report.md",
    ]
    return [(relative_path, run_dir / relative_path) for relative_path in relative_paths]

def validation_counts(run_id: str) -> dict[str, str]:
    report = OUTPUT_ROOT / run_id / "derived" / "radar_cards" / "radar-card-validation-report.md"
    labels = ["Radar-card count", "Passed count", "Warning count", "Failed count"]
    counts = {}
    if not report.exists():
        return counts
    for line in report.read_text(encoding="utf-8", errors="ignore").splitlines():
        for label in labels:
            prefix = label + ":"
            if line.startswith(prefix):
                counts[label] = line[len(prefix):].strip()
    return counts

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

for key in ["safety_audit_output", "create_run_output", "workspace_dashboard_output", "upload_output", "youtube_intake_output", "operator_brief_output", "pipeline_smoke_output"]:
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
    st.subheader("Run summary")
    st.table([
        {"path": relative_path, "status": "available" if path.exists() else "missing"}
        for relative_path, path in run_summary_files(selected_run)
    ])
    counts = validation_counts(selected_run)
    if counts:
        st.write(
            "Radar-card validation:",
            "count " + counts.get("Radar-card count", "not available"),
            "| passed " + counts.get("Passed count", "not available"),
            "| warnings " + counts.get("Warning count", "not available"),
            "| failed " + counts.get("Failed count", "not available"),
        )

st.subheader("Create local run folder")
run_id = st.text_input("Run ID", value="ui-smoke-test-001")
if st.button("Create run folder"):
    st.session_state.create_run_output = run_command(["python3", "apps/youtube_mining/scripts/create_run_folder.py", run_id])
    st.rerun()
if st.session_state.create_run_output:
    st.code(st.session_state.create_run_output)

st.subheader("YouTube source intake")
if selected_run:
    youtube_input = st.text_input("YouTube URL or video ID")
    if st.button("Add YouTube source"):
        if youtube_input.strip():
            st.session_state.youtube_intake_output = run_command([
                "python3",
                "apps/youtube_mining/scripts/intake_youtube_source.py",
                selected_run,
                "--url",
                youtube_input.strip(),
            ])
            st.rerun()
        else:
            st.session_state.youtube_intake_output = "ERROR YouTube URL or video ID is required."
if st.session_state.youtube_intake_output:
    st.code(st.session_state.youtube_intake_output)

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

st.subheader("Derived placeholder")
if selected_run:
    if st.button("Build derived placeholder"):
        st.session_state.derived_output = run_command(["python3", "apps/youtube_mining/scripts/build_derived_placeholder.py", selected_run])
    if "derived_output" in st.session_state and st.session_state.derived_output:
        st.code(st.session_state.derived_output)

st.subheader("Operator brief placeholder")
if selected_run:
    if st.button("Build operator brief placeholder"):
        st.session_state.operator_brief_output = run_command(["python3", "apps/youtube_mining/scripts/build_operator_brief_placeholder.py", selected_run])
    if st.session_state.operator_brief_output:
        st.code(st.session_state.operator_brief_output)

    brief = operator_brief_path(selected_run)
    if brief.exists():
        st.write("Operator brief: available")
        st.write("handoffs/operator_brief.md")
        st.markdown(brief.read_text(encoding="utf-8", errors="ignore"))
    else:
        st.write("Operator brief: not available yet")

st.subheader("Full pipeline smoke test")
if selected_run:
    smoke_model = st.text_input("Smoke model", value="qwen2.5:7b")
    smoke_limit = st.number_input("Smoke limit", min_value=1, value=1, step=1)
    smoke_skip_model = st.checkbox("Skip model", value=False)
    if st.button("Run full pipeline smoke"):
        command = [
            "python3",
            "apps/youtube_mining/scripts/run_ytm_pipeline_smoke.py",
            selected_run,
            "--model",
            smoke_model.strip() or "qwen2.5:7b",
            "--limit",
            str(int(smoke_limit)),
        ]
        if smoke_skip_model:
            command.append("--skip-model")
        st.session_state.pipeline_smoke_output = run_command(command)

    if st.session_state.pipeline_smoke_output:
        st.code(st.session_state.pipeline_smoke_output)

    smoke_report = pipeline_smoke_report_path(selected_run)
    if smoke_report.exists():
        st.write("Pipeline smoke report: available")
        st.write("handoffs/ytm_pipeline_smoke_report.md")
    else:
        st.write("Pipeline smoke report: not available yet")

st.subheader("Workspace dashboard")
if st.button("Run workspace dashboard"):
    st.session_state.workspace_dashboard_output = run_command(["python3", "scripts/status_dashboard.py"])
if st.session_state.workspace_dashboard_output:
    st.code(st.session_state.workspace_dashboard_output)

st.subheader("Current limitations")
st.markdown("- No YouTube download yet\n- No transcript processing yet\n- No local model call yet\n- No radar-card generation yet\n- No handoff generation yet")
