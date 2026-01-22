
import streamlit as st
import subprocess
import tempfile
import os
import shlex
from pathlib import Path
import threading
import time

st.set_page_config(page_title="Promptfoo Red Team (Streamlit)", layout="wide")

st.title("Promptfoo Red Team — Streamlit UI")
st.markdown(
    """
Upload or edit a `promptfooconfig.yaml` (Promptfoo redteam config).  
This UI will save the config, run `npx promptfoo redteam run` and stream output logs.
"""
)

with st.sidebar:
    st.header("Controls")
    uploaded = st.file_uploader("Upload promptfooconfig.yaml", type=["yaml", "yml"], accept_multiple_files=False)
    config_text = st.text_area("Or paste / edit config text here (overrides upload)", height=250)
    auto_run = st.checkbox("Auto-run after saving config", value=False)
    run_button = st.button("Run redteam now")

# decide config content
config_content = None
if uploaded is not None:
    config_content = uploaded.read().decode("utf-8")
if config_text and config_text.strip():
    config_content = config_text

if not config_content:
    st.info("No config provided. You can upload a `promptfooconfig.yaml` or paste its contents in the text area.")
    st.stop()

# Save config to a temp directory (persist inside app workspace)
workdir = Path("promptfoo_workspace")
workdir.mkdir(exist_ok=True)
config_path = workdir / "promptfooconfig.yaml"
config_path.write_text(config_content, encoding="utf-8")
st.success(f"Saved config to `{config_path}`")

log_container = st.empty()

def run_promptfoo(cmd_args, out_element):
    """
    Runs a command (list) and streams output to the given streamlit element.
    Returns (returncode, captured_text)
    """
    # Use a text area to show streaming output
    placeholder = out_element.container()
    text_area = placeholder.text_area("Promptfoo logs", value="", height=420)
    # We'll update via the placeholder's markdown each line appended
    proc = subprocess.Popen(
        cmd_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        cwd=str(workdir),
    )

    captured = []
    try:
        for line in proc.stdout:
            captured.append(line)
            # update text area with new content
            placeholder.text_area("Promptfoo logs", value="".join(captured), height=420)
    except Exception as ex:
        captured.append(f"\n[ERROR] {ex}\n")
        placeholder.text_area("Promptfoo logs", value="".join(captured), height=420)
    proc.wait()
    return proc.returncode, "".join(captured)

def run_in_thread(args_list):
    # thread runner to avoid blocking the Streamlit main thread
    status = st.empty()
    status.info("Running red team... this may take a while.")
    rc, out = run_promptfoo(args_list, log_container)
    if rc == 0:
        status.success("Promptfoo finished successfully.")
    else:
        status.error(f"Promptfoo exited with code {rc}. See logs above.")
    # If a report can be generated, user can run `npx promptfoo redteam report` manually;
    # we try to run it automatically if present.
    return rc, out

if run_button or auto_run:
    # Build the npx command. We assume Node & npx are available in PATH.
    st.info("Attempting to run `npx promptfoo@latest redteam run` using local npx.")
    args = shlex.split("npx promptfoo@latest redteam run --config promptfooconfig.yaml")
    # Run in background thread so streamlit remains responsive
    thread = threading.Thread(target=run_in_thread, args=(args,), daemon=True)
    thread.start()
    # optionally wait a short time to allow logs to appear
    time.sleep(0.2)

st.markdown("---")
st.subheader("Quick troubleshooting / notes")
st.markdown(
    """
- This UI calls the Promptfoo CLI via `npx` (Node.js 20+ required). If `npx` is not installed in the environment, the run will fail.  
- To deploy reliably in the cloud, use the provided `Dockerfile` (installs Node 20 and Python).  
- After runs, Promptfoo writes artifacts (e.g., `redteam.yaml`, report files) under the working directory; you can download them from the app host or browse them if you mount persistence.
"""
)
