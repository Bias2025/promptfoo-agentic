import streamlit as st
import yaml
import subprocess
from pathlib import Path
import shlex
import threading

st.set_page_config(page_title="Red Team Wizard", layout="wide")

st.title("Agentic Red Team ")

WORKDIR = Path("promptfoo_workspace")
WORKDIR.mkdir(exist_ok=True)
CONFIG_PATH = WORKDIR / "promptfooconfig.yaml"

# -----------------------------
# Step 1: Purpose & target
# -----------------------------
st.header("1️⃣ Describe your target application")

purpose = st.text_area(
    "Purpose (required)",
    placeholder="Example: Customer support chatbot for banking queries",
)

target_type = st.selectbox(
    "Target type",
    ["HTTP API", "OpenAI-compatible model", "Local / custom code"],
)

# -----------------------------
# Step 2: Connection details
# -----------------------------
st.header("2️⃣ Configure how Promptfoo talks to your target")

target_config = {}

if target_type == "HTTP API":
    target_config["type"] = "http"
    target_config["url"] = st.text_input("Endpoint URL", placeholder="https://api.example.com/chat")
    target_config["method"] = st.selectbox("HTTP method", ["POST", "GET"])
    target_config["headers"] = st.text_area(
        "Headers (YAML format)",
        placeholder="Authorization: Bearer YOUR_TOKEN",
    )

elif target_type == "OpenAI-compatible model":
    target_config["type"] = "openai"
    target_config["model"] = st.text_input("Model name", value="gpt-4.1-mini")
    target_config["apiBase"] = st.text_input(
        "API base (optional)",
        placeholder="https://api.openai.com/v1",
    )

else:
    target_config["type"] = "custom"
    target_config["entrypoint"] = st.text_input(
        "Entrypoint script",
        placeholder="python my_model.py",
    )

# -----------------------------
# Step 3: Plugins
# -----------------------------
st.header("3️⃣ Select adversarial plugins")

plugin_presets = {
    "Default": [
        "prompt-injection",
        "jailbreak",
        "policy-violation",
        "roleplay",
    ],
    "Injection-heavy": [
        "prompt-injection",
        "indirect-prompt-injection",
    ],
    "Safety-focused": [
        "policy-violation",
        "harmful-content",
    ],
}

preset = st.selectbox("Plugin preset", list(plugin_presets.keys()))
plugins = plugin_presets[preset]

st.code("\n".join(plugins), language="text")

# -----------------------------
# Step 4: Strategies
# -----------------------------
st.header("4️⃣ Select attack strategies")

strategies = st.multiselect(
    "Strategies",
    [
        "base64",
        "roleplay",
        "translation",
        "encoding",
        "context-shifting",
    ],
    default=["roleplay", "context-shifting"],
)

# -----------------------------
# Step 5: Review & generate
# -----------------------------
st.header("5️⃣ Review & generate config")

if st.button("Generate promptfooconfig.yaml"):
    if not purpose.strip():
        st.error("Purpose is required.")
        st.stop()

    config = {
        "purpose": purpose,
        "targets": [
            {
                "id": "target-app",
                **target_config,
            }
        ],
        "redteam": {
            "plugins": plugins,
            "strategies": strategies,
        },
    }

    CONFIG_PATH.write_text(yaml.dump(config, sort_keys=False))
    st.success(f"Configuration written to {CONFIG_PATH}")

    st.subheader("Generated config")
    st.code(yaml.dump(config, sort_keys=False), language="yaml")

# -----------------------------
# Run redteam
# -----------------------------
st.header("🚨 Run red team")

def run_redteam():
    cmd = shlex.split("npx promptfoo@latest redteam run --config promptfooconfig.yaml")
    subprocess.run(cmd, cwd=WORKDIR)

if st.button("Run redteam now"):
    if not CONFIG_PATH.exists():
        st.error("Generate a config first.")
    else:
        threading.Thread(target=run_redteam, daemon=True).start()
        st.info("Red team running… check logs in the terminal / container output.")
