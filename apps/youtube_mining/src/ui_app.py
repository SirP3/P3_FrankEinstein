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

UI_TEXT = {
    "en": {
        "title": "P3FE YouTube Mining v0.2",
        "caption": "Safety-first local source adapter shell",
        "intro": "Safety-first local YTM operator UI. Source/runtime content stays local-only and is not previewed as raw content.",
        "operator_mode": "YTM Operator Mode",
        "operator_caption": "Run one controlled YTM source intake. This is not channel-scale automation.",
        "source_section": "Source",
        "run_settings": "Run settings",
        "operator_actions": "Operator actions",
        "safe_status": "Safe status",
        "advanced": "Advanced",
        "command_output": "Command output",
        "operator_run_id": "Operator run ID",
        "operator_source_input": "Operator source input",
        "single_input": "Single URL/video ID",
        "list_file_input": "List-file path",
        "operator_url": "Operator YouTube URL or video ID",
        "operator_list_file": "Operator list-file path",
        "list_file_caption": "Use a local-only text file path. File content is not previewed in the UI.",
        "operator_model": "Operator model",
        "operator_limit": "Operator limit",
        "skip_model": "Skip model",
        "limit_caption": "Limit is the processing safety cap. Keep it small while validating list-file input.",
        "run_pipeline": "Run YTM pipeline",
        "source_required": "ERROR source input is required.",
        "summary_available": "YTM run summary: available",
        "summary_missing": "YTM run summary: not available yet",
        "resume_status": "Resume / skip-existing status",
        "output_folder": "Output folder",
        "output_available": "Output folder: available",
        "open_finder": "Open output folder in Finder",
        "output_missing": "output folder not found yet",
        "runtime_safety": "Runtime boundary and safety",
        "runtime_boundary": "Runtime boundary",
        "runtime_note": "Runtime output is local-only and ignored by git.",
        "safety_status": "Safety status",
        "run_safety_audit": "Run safety audit",
        "local_runs": "Local YTM runs",
        "run_count": "Run count:",
        "selected_run": "Selected run",
        "no_runs": "No local runs found.",
        "selected_run_status": "Selected run status",
        "validation": "Radar-card validation:",
        "legacy_url": "Legacy URL pipeline control",
        "url_run_id": "URL pipeline run ID",
        "url_input": "URL pipeline YouTube URL or video ID",
        "url_model": "URL pipeline model",
        "url_limit": "URL pipeline limit",
        "url_skip_model": "URL pipeline skip model",
        "run_url_pipeline": "Run URL pipeline",
        "url_required": "ERROR YouTube URL or video ID is required.",
        "safe_preview": "YTM safe final summary preview",
        "manual_controls": "Optional manual controls",
        "create_run": "Create local run folder",
        "run_id": "Run ID",
        "create_run_folder": "Create run folder",
        "youtube_intake": "YouTube source intake",
        "youtube_input": "YouTube URL or video ID",
        "add_youtube": "Add YouTube source",
        "manual_intake": "Manual source intake",
        "upload_source": "Add one local-only source file to selected run",
        "save_upload": "Save uploaded source to selected run",
        "source_status": "Source status",
        "source_file_count": "Source file count:",
        "no_source_files": "No source files in this run yet.",
        "derived_placeholder": "Derived placeholder",
        "build_derived": "Build derived placeholder",
        "operator_brief_placeholder": "Operator brief placeholder",
        "build_operator_brief": "Build operator brief placeholder",
        "operator_brief_available": "Operator brief: available",
        "operator_brief_missing": "Operator brief: not available yet",
        "smoke_test": "Full pipeline smoke test",
        "smoke_model": "Smoke model",
        "smoke_limit": "Smoke limit",
        "run_smoke": "Run full pipeline smoke",
        "smoke_available": "Pipeline smoke report: available",
        "smoke_missing": "Pipeline smoke report: not available yet",
        "workspace_dashboard": "Workspace dashboard",
        "run_workspace_dashboard": "Run workspace dashboard",
        "limitations": "Current limitations",
        "limitations_text": "- Not production service\n- No channel-scale automation\n- No RR / Reddit Radar implementation yet\n- Runtime/source content stays local-only\n- Local model output is not source of truth",
    },
    "hu": {
        "title": "P3FE YouTube Mining v0.2",
        "caption": "Biztonságos, helyi forrásadapter",
        "intro": "Biztonságos helyi YTM operátori felület. A forrás- és runtime tartalom lokális marad, nyers tartalomként nem jelenik meg.",
        "operator_mode": "YTM Operátori mód",
        "operator_caption": "Egy kontrollált YTM forrásfuttatás indítása. Ez nem csatornaszintű automatizálás.",
        "source_section": "Forrás",
        "run_settings": "Futási beállítások",
        "operator_actions": "Műveletek",
        "safe_status": "Biztonságos státusz",
        "advanced": "Haladó",
        "command_output": "Parancskimenet",
        "operator_run_id": "Operátori run ID",
        "operator_source_input": "Operátori forrásbemenet",
        "single_input": "Egy URL/video ID",
        "list_file_input": "Listafájl útvonal",
        "operator_url": "YouTube URL vagy video ID",
        "operator_list_file": "Listafájl helyi útvonala",
        "list_file_caption": "Helyi, lokális listafájl útvonal. A fájl tartalmát a UI nem jeleníti meg.",
        "operator_model": "Operátori modell",
        "operator_limit": "Operátori limit",
        "skip_model": "Modell kihagyása",
        "limit_caption": "A limit a feldolgozási biztonsági sapka. Listafájl tesztnél maradjon kicsi.",
        "run_pipeline": "YTM pipeline indítása",
        "source_required": "HIBA: forrásbemenet szükséges.",
        "summary_available": "YTM run summary: elérhető",
        "summary_missing": "YTM run summary: még nem elérhető",
        "resume_status": "Folytatás / meglévők kihagyása",
        "output_folder": "Kimeneti mappa",
        "output_available": "Kimeneti mappa: elérhető",
        "open_finder": "Kimeneti mappa megnyitása Finderben",
        "output_missing": "kimeneti mappa még nem található",
        "runtime_safety": "Runtime határ és biztonság",
        "runtime_boundary": "Runtime határ",
        "runtime_note": "A runtime output lokális és git által ignorált.",
        "safety_status": "Biztonsági státusz",
        "run_safety_audit": "Safety audit futtatása",
        "local_runs": "Helyi YTM futások",
        "run_count": "Run darabszám:",
        "selected_run": "Kiválasztott run",
        "no_runs": "Nincs helyi run.",
        "selected_run_status": "Kiválasztott run státusz",
        "validation": "Radar-card validáció:",
        "legacy_url": "Régi URL pipeline kontroll",
        "url_run_id": "URL pipeline run ID",
        "url_input": "URL pipeline YouTube URL vagy video ID",
        "url_model": "URL pipeline modell",
        "url_limit": "URL pipeline limit",
        "url_skip_model": "URL pipeline modell kihagyása",
        "run_url_pipeline": "URL pipeline indítása",
        "url_required": "HIBA: YouTube URL vagy video ID szükséges.",
        "safe_preview": "YTM biztonságos végső összefoglaló előnézet",
        "manual_controls": "Opcionális manuális vezérlők",
        "create_run": "Helyi run mappa létrehozása",
        "run_id": "Run ID",
        "create_run_folder": "Run mappa létrehozása",
        "youtube_intake": "YouTube forrásbevitel",
        "youtube_input": "YouTube URL vagy video ID",
        "add_youtube": "YouTube forrás hozzáadása",
        "manual_intake": "Manuális forrásbevitel",
        "upload_source": "Egy lokális forrásfájl hozzáadása a kiválasztott runhoz",
        "save_upload": "Feltöltött forrás mentése a kiválasztott runhoz",
        "source_status": "Forrás státusz",
        "source_file_count": "Forrásfájlok száma:",
        "no_source_files": "Ebben a runban még nincs forrásfájl.",
        "derived_placeholder": "Derived placeholder",
        "build_derived": "Derived placeholder építése",
        "operator_brief_placeholder": "Operator brief placeholder",
        "build_operator_brief": "Operator brief placeholder építése",
        "operator_brief_available": "Operator brief: elérhető",
        "operator_brief_missing": "Operator brief: még nem elérhető",
        "smoke_test": "Teljes pipeline smoke teszt",
        "smoke_model": "Smoke modell",
        "smoke_limit": "Smoke limit",
        "run_smoke": "Teljes pipeline smoke futtatása",
        "smoke_available": "Pipeline smoke report: elérhető",
        "smoke_missing": "Pipeline smoke report: még nem elérhető",
        "workspace_dashboard": "Workspace dashboard",
        "run_workspace_dashboard": "Workspace dashboard futtatása",
        "limitations": "Aktuális korlátok",
        "limitations_text": "- Nem production service\n- Nincs csatornaszintű automatizálás\n- RR / Reddit Radar még nincs implementálva\n- Runtime/forrás tartalom lokális marad\n- A helyi modell output nem source of truth",
    },
}

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

language_choice = st.sidebar.selectbox("Nyelv / Language", ["Magyar", "English"], key="ui_language")
UI_LANG = "hu" if language_choice == "Magyar" else "en"

def tr(key: str) -> str:
    return UI_TEXT[UI_LANG].get(key, UI_TEXT["en"].get(key, key))

st.title(tr("title"))
st.caption(tr("caption"))
st.info(tr("intro"))

st.subheader(tr("operator_mode"))
st.caption(tr("operator_caption"))

st.markdown("#### " + tr("source_section"))
operator_input_mode = st.radio(
    tr("operator_source_input"),
    ["single", "list-file"],
    horizontal=True,
    format_func=lambda value: tr("single_input") if value == "single" else tr("list_file_input"),
    key="operator_input_mode",
)

operator_url = ""
operator_list_file = ""
if operator_input_mode == "single":
    operator_url = st.text_input(tr("operator_url"), key="operator_url")
else:
    operator_list_file = st.text_input(tr("operator_list_file"), key="operator_list_file")
    st.caption(tr("list_file_caption"))

st.markdown("#### " + tr("run_settings"))
settings_col0, settings_col1, settings_col2, settings_col3 = st.columns([1.4, 1, 0.7, 0.7])
with settings_col0:
    operator_run_id = st.text_input(tr("operator_run_id"), value="ytm-operator-001", key="operator_run_id")
with settings_col1:
    operator_model = st.text_input(tr("operator_model"), value="qwen2.5:7b", key="operator_model")
with settings_col2:
    operator_limit = st.number_input(tr("operator_limit"), min_value=1, value=1, step=1, key="operator_limit")
with settings_col3:
    operator_skip_model = st.checkbox(tr("skip_model"), value=False, key="operator_skip_model")
st.caption(tr("limit_caption"))

st.markdown("#### " + tr("operator_actions"))
if st.button(tr("run_pipeline"), key="operator_run_pipeline"):
    operator_source_value = operator_url.strip() if operator_input_mode == "single" else operator_list_file.strip()
    if operator_source_value:
        command = [
            "python3",
            "apps/youtube_mining/scripts/run_ytm_url_pipeline.py",
            operator_run_id,
            "--url" if operator_input_mode == "single" else "--list-file",
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
        st.session_state.operator_mode_output = tr("source_required")

if st.session_state.operator_mode_output:
    with st.expander(tr("command_output")):
        st.code(st.session_state.operator_mode_output)

st.markdown("#### " + tr("safe_status"))
operator_summary = ytm_run_summary_path(safe_run_id(operator_run_id))
if operator_summary.exists():
    st.write(tr("summary_available"))
    st.write("handoffs/ytm_run_summary.md")
else:
    st.write(tr("summary_missing"))

st.table([{"field": key, "value": value} for key, value in safe_summary_preview(operator_run_id).items()])

with st.expander(tr("resume_status")):
    st.table([{"field": key, "value": value} for key, value in operator_resume_status(operator_run_id).items()])

operator_output_folder = run_output_folder(operator_run_id)
with st.expander(tr("output_folder")):
    st.code(str(operator_output_folder))
    if operator_output_folder.exists():
        st.write(tr("output_available"))
        if sys.platform == "darwin" and st.button(tr("open_finder"), key="operator_open_output_folder"):
            subprocess.run(["open", str(operator_output_folder)], check=False)
    else:
        st.write(tr("output_missing"))

st.subheader(tr("advanced"))

with st.expander(tr("runtime_safety")):
    st.subheader(tr("runtime_boundary"))
    st.code(str(OUTPUT_ROOT))
    st.write(tr("runtime_note"))
    st.subheader(tr("safety_status"))
    if st.button(tr("run_safety_audit"), key="run_safety_audit"):
        st.session_state.safety_audit_output = run_command(["python3", "scripts/safety/public_safety_audit.py"])
    if st.session_state.safety_audit_output:
        st.code(st.session_state.safety_audit_output)

st.subheader(tr("local_runs"))

runs = list_runs()
if runs:
    st.write(tr("run_count"), len(runs))
    selected_run = st.selectbox(tr("selected_run"), runs, index=len(runs) - 1, key="selected_run")
else:
    st.write(tr("no_runs"))
    selected_run = ""

if selected_run:
    with st.expander(tr("selected_run_status")):
        st.table([
            {"path": relative_path, "status": "available" if path.exists() else "missing"}
            for relative_path, path in run_summary_files(selected_run)
        ])
        counts = validation_counts(selected_run)
        if counts:
            st.write(
                tr("validation"),
                "count " + counts.get("Radar-card count", "not available"),
                "| passed " + counts.get("Passed count", "not available"),
                "| warnings " + counts.get("Warning count", "not available"),
                "| failed " + counts.get("Failed count", "not available"),
            )

with st.expander(tr("legacy_url")):
    url_pipeline_run_id = st.text_input(tr("url_run_id"), value="ytm-ui-url-test-001", key="url_pipeline_run_id")
    url_pipeline_input = st.text_input(tr("url_input"), key="url_pipeline_input")
    url_pipeline_model = st.text_input(tr("url_model"), value="qwen2.5:7b", key="url_pipeline_model")
    url_pipeline_limit = st.number_input(tr("url_limit"), min_value=1, value=1, step=1, key="url_pipeline_limit")
    url_pipeline_skip_model = st.checkbox(tr("url_skip_model"), value=False, key="url_pipeline_skip_model")
    if st.button(tr("run_url_pipeline"), key="url_pipeline_run_button"):
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
            st.session_state.url_pipeline_output = tr("url_required")

    if st.session_state.url_pipeline_output:
        st.code(st.session_state.url_pipeline_output)

    url_pipeline_preview = safe_summary_preview(url_pipeline_run_id)
    st.write(tr("safe_preview"))
    st.table([{"field": key, "value": value} for key, value in url_pipeline_preview.items()])

with st.expander(tr("manual_controls")):
    st.subheader(tr("create_run"))
    run_id = st.text_input(tr("run_id"), value="ui-smoke-test-001", key="manual_run_id")
    if st.button(tr("create_run_folder"), key="manual_create_run_folder"):
        st.session_state.create_run_output = run_command(["python3", "apps/youtube_mining/scripts/create_run_folder.py", run_id])
        st.rerun()
    if st.session_state.create_run_output:
        st.code(st.session_state.create_run_output)

    st.subheader(tr("youtube_intake"))
    if selected_run:
        youtube_input = st.text_input(tr("youtube_input"), key="manual_youtube_input")
        if st.button(tr("add_youtube"), key="manual_add_youtube_source"):
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
                st.session_state.youtube_intake_output = tr("url_required")
    if st.session_state.youtube_intake_output:
        st.code(st.session_state.youtube_intake_output)

    st.subheader(tr("manual_intake"))
    if selected_run:
        uploaded = st.file_uploader(tr("upload_source"), type=["md", "txt", "vtt", "srt", "json"], key="manual_source_upload")
        if uploaded is not None and st.button(tr("save_upload"), key="manual_save_source_upload"):
            try:
                target = write_uploaded_source(selected_run, uploaded)
                st.session_state.upload_output = "SAVED " + str(target)
                st.rerun()
            except Exception as exc:
                st.session_state.upload_output = "ERROR " + str(exc)
    if st.session_state.upload_output:
        st.code(st.session_state.upload_output)

    if selected_run:
        st.subheader(tr("source_status"))
        files = source_files(selected_run)
        st.write(tr("selected_run") + ":", selected_run)
        st.write(tr("source_file_count"), len(files))
        if files:
            for file in files:
                st.write("-", file.relative_to(OUTPUT_ROOT / selected_run))
        else:
            st.write(tr("no_source_files"))

    st.subheader(tr("derived_placeholder"))
    if selected_run:
        if st.button(tr("build_derived"), key="manual_build_derived_placeholder"):
            st.session_state.derived_output = run_command(["python3", "apps/youtube_mining/scripts/build_derived_placeholder.py", selected_run])
        if "derived_output" in st.session_state and st.session_state.derived_output:
            st.code(st.session_state.derived_output)

    st.subheader(tr("operator_brief_placeholder"))
    if selected_run:
        if st.button(tr("build_operator_brief"), key="manual_build_operator_brief"):
            st.session_state.operator_brief_output = run_command(["python3", "apps/youtube_mining/scripts/build_operator_brief_placeholder.py", selected_run])
        if st.session_state.operator_brief_output:
            st.code(st.session_state.operator_brief_output)

        brief = operator_brief_path(selected_run)
        if brief.exists():
            st.write(tr("operator_brief_available"))
            st.write("handoffs/operator_brief.md")
            st.markdown(brief.read_text(encoding="utf-8", errors="ignore"))
        else:
            st.write(tr("operator_brief_missing"))

    st.subheader(tr("smoke_test"))
    if selected_run:
        smoke_model = st.text_input(tr("smoke_model"), value="qwen2.5:7b", key="manual_smoke_model")
        smoke_limit = st.number_input(tr("smoke_limit"), min_value=1, value=1, step=1, key="manual_smoke_limit")
        smoke_skip_model = st.checkbox(tr("skip_model"), value=False, key="manual_smoke_skip_model")
        if st.button(tr("run_smoke"), key="manual_run_pipeline_smoke"):
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
            st.write(tr("smoke_available"))
            st.write("handoffs/ytm_pipeline_smoke_report.md")
        else:
            st.write(tr("smoke_missing"))

    st.subheader(tr("workspace_dashboard"))
    if st.button(tr("run_workspace_dashboard"), key="manual_run_workspace_dashboard"):
        st.session_state.workspace_dashboard_output = run_command(["python3", "scripts/status_dashboard.py"])
    if st.session_state.workspace_dashboard_output:
        st.code(st.session_state.workspace_dashboard_output)

with st.expander(tr("limitations")):
    st.markdown(tr("limitations_text"))
