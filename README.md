# Promptfoo Red Team — Streamlit UI

## What this does
- Lets you upload/edit a `promptfooconfig.yaml`
- Runs `npx promptfoo@latest redteam run --config promptfooconfig.yaml`
- Streams the CLI logs into the Streamlit UI

## Important prerequisites
- Promptfoo is a Node.js tool and requires Node.js 20+ (the docs show Node 20+ as a prerequisite). :contentReference[oaicite:3]{index=3}
- The official quickstart uses the CLI: `npx promptfoo@latest redteam setup` and `npx promptfoo@latest redteam run`. This app invokes `npx` under the hood. :contentReference[oaicite:4]{index=4}

## Deploy
1. Build locally:
