---
name: kimi-ai
description: Interacts with the Kimi K3 (moonshotai/Kimi-K3) model hosted on the Modal proxy endpoint for technical reasoning, code analysis, and high-performance LLM completions.
---

# Kimi K3 Skill

Use this skill when you need to query the Kimi K3 model (`moonshotai/Kimi-K3`) hosted via the Modal proxy endpoint.

## How to Call Kimi K3 in Python
Use the project client in `kimi_client.py`:

```python
from kimi_client import ask_kimi

response = ask_kimi("Explain your question here")
print(response)
```

## CLI Execution
Run directly in your terminal:
```bash
python kimi_client.py "Your prompt here"
```

## Configuration
Requires `MODAL_PROXY_TOKEN_ID` and `MODAL_PROXY_TOKEN_SECRET` in `.env`.
