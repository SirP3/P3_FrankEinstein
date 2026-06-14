from pathlib import Path
import re
import subprocess
import sys

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

def concise_output(value: str, max_chars: int = 1600) -> str:
    value = value.strip()
    if len(value) <= max_chars:
        return value
    return "... trimmed ...\n" + value[-max_chars:].strip()

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

def ytm_run_summary_path(run_id: str) -> Path:
    return OUTPUT_ROOT / run_id / "handoffs" / "ytm_run_summary.md"

def run_output_folder(run_id: str) -> Path:
    return OUTPUT_ROOT / safe_run_id(run_id)

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
        "handoffs/ytm_run_summary.md",
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

def read_log_values(path: Path, labels: list[str]) -> dict[str, str]:
    values = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        for label in labels:
            prefix = label + ":"
            if line.startswith(prefix):
                values[label] = line[len(prefix):].strip()
    return values

def operator_resume_status(run_id: str) -> dict[str, str]:
    run_id = safe_run_id(run_id)
    run_dir = OUTPUT_ROOT / run_id
    intake = read_log_values(
        run_dir / "source" / "transcript-intake-log.md",
        ["Selected video count", "Processed video count", "Skipped existing count", "Processing limit"],
    )
    conversion = read_log_values(
        run_dir / "derived" / "transcript-conversion-log.md",
        ["Processed file count", "Skipped existing count", "Processing limit"],
    )
    summary = read_log_values(run_dir / "handoffs" / "ytm_run_summary.md", ["Final status"])
    return {
        "selected": intake.get("Selected video count", "not available"),
        "transcript processed": intake.get("Processed video count", "not available"),
        "transcript skipped existing": intake.get("Skipped existing count", "not available"),
        "conversion processed": conversion.get("Processed file count", "not available"),
        "conversion skipped existing": conversion.get("Skipped existing count", "not available"),
        "limit cap": intake.get("Processing limit", conversion.get("Processing limit", "not available")),
        "final status": summary.get("Final status", "not available"),
    }

def safe_summary_preview(run_id: str) -> dict[str, str]:
    run_id = safe_run_id(run_id)
    summary = ytm_run_summary_path(run_id)
    counts = validation_counts(run_id)
    preview = {
        "final status": "available" if summary.exists() else "summary not found yet",
        "transcript count": "not available",
        "radar-card count": counts.get("Radar-card count", "not available"),
        "passed": counts.get("Passed count", "not available"),
        "warnings": counts.get("Warning count", "not available"),
        "failed": counts.get("Failed count", "not available"),
        "output path": str(summary),
        "policy note": "Public Source, Private Processing, Clean Output — source/runtime content is not displayed in UI preview.",
    }

    transcript_index = OUTPUT_ROOT / run_id / "derived" / "transcript_index.md"
    if transcript_index.exists():
        transcript_lines = transcript_index.read_text(encoding="utf-8", errors="ignore").splitlines()
        preview["transcript count"] = str(sum(1 for line in transcript_lines if line.strip().startswith("- ")))

    return preview

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

for key in ["safety_audit_output", "create_run_output", "workspace_dashboard_output", "upload_output", "youtube_intake_output", "operator_brief_output", "pipeline_smoke_output", "url_pipeline_output", "operator_mode_output"]:
    if key not in st.session_state:
        st.session_state[key] = ""

st.set_page_config(page_title="P3FE YTM v0.2", layout="wide")

st.title("P3FE YouTube Mining v0.2")
st.caption("Safety-first local source adapter shell")
st.info("Safety-first local YTM operator UI. Source/runtime content stays local-only and is not previewed as raw content.")

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

st.subheader("YTM Operator Mode")
st.caption("Single-source or local list-file source intake. This is not channel-scale automation.")
operator_run_id = st.text_input("Operator run ID", value="ytm-operator-001")
operator_input_mode = st.radio("Operator source input", ["Single URL/video ID", "List-file path"], horizontal=True)
operator_url = ""
operator_list_file = ""
if operator_input_mode == "Single URL/video ID":
    operator_url = st.text_input("Operator YouTube URL or video ID")
else:
    operator_list_file = st.text_input("Operator list-file path")
    st.caption("Use a local-only text file path. File content is not previewed in the UI.")
operator_model = st.text_input("Operator model", value="qwen2.5:7b")
operator_limit = st.number_input("Operator limit", min_value=1, value=1, step=1)
st.caption("Limit is the processing safety cap. Keep it small while validating list-file input.")
operator_skip_model = st.checkbox("Operator skip model", value=False)
if st.button("Run YTM pipeline"):
    operator_source_value = operator_url.strip() if operator_input_mode == "Single URL/video ID" else operator_list_file.strip()
    if operator_source_value:
        command = [
            "python3",
            "apps/youtube_mining/scripts/run_ytm_url_pipeline.py",
            operator_run_id,
            "--url" if operator_input_mode == "Single URL/video ID" else "--list-file",
            operator_source_value,
            "--model",
            operator_model.strip() or "qwen2.5:7b",
            "--limit",
            str(int(operator_limit)),
        ]
        if operator_skip_model:
            command.append("--skip-model")
        st.session_state.operator_mode_output = concise_output(run_command(command))
    else:
        st.session_state.operator_mode_output = "ERROR source input is required."

if st.session_state.operator_mode_output:
    st.code(st.session_state.operator_mode_output)

operator_summary = ytm_run_summary_path(safe_run_id(operator_run_id))
if operator_summary.exists():
    st.write("YTM run summary: available")
    st.write("handoffs/ytm_run_summary.md")
else:
    st.write("YTM run summary: not available yet")

st.write("Resume / skip-existing status")
st.table([{"field": key, "value": value} for key, value in operator_resume_status(operator_run_id).items()])

operator_output_folder = run_output_folder(operator_run_id)
st.write("Output folder")
st.code(str(operator_output_folder))
if operator_output_folder.exists():
    st.write("Output folder: available")
    if sys.platform == "darwin" and st.button("Open output folder in Finder"):
        subprocess.run(["open", str(operator_output_folder)], check=False)
else:
    st.write("output folder not found yet")

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

st.subheader("Run full pipeline from YouTube URL")
url_pipeline_run_id = st.text_input("URL pipeline run ID", value="ytm-ui-url-test-001")
url_pipeline_input = st.text_input("URL pipeline YouTube URL or video ID")
url_pipeline_model = st.text_input("URL pipeline model", value="qwen2.5:7b")
url_pipeline_limit = st.number_input("URL pipeline limit", min_value=1, value=1, step=1)
url_pipeline_skip_model = st.checkbox("URL pipeline skip model", value=False)
if st.button("Run URL pipeline"):
    if url_pipeline_input.strip():
        command = [
            "python3",
            "apps/youtube_mining/scripts/run_ytm_url_pipeline.py",
            url_pipeline_run_id,
            "--url",
            url_pipeline_input.strip(),
            "--model",
            url_pipeline_model.strip() or "qwen2.5:7b",
            "--limit",
            str(int(url_pipeline_limit)),
        ]
        if url_pipeline_skip_model:
            command.append("--skip-model")
        st.session_state.url_pipeline_output = run_command(command)
    else:
        st.session_state.url_pipeline_output = "ERROR YouTube URL or video ID is required."

if st.session_state.url_pipeline_output:
    st.code(st.session_state.url_pipeline_output)

url_pipeline_preview = safe_summary_preview(url_pipeline_run_id)
st.write("YTM safe final summary preview")
st.table([{"field": key, "value": value} for key, value in url_pipeline_preview.items()])

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
