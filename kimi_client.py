"""
Kimi K3 / Modal Proxy Client for Antigravity & Python Applications.

Usage:
  # As a module:
  from kimi_client import get_kimi_client, ask_kimi

  response = ask_kimi("Explain Python decorators in 3 bullets")
  print(response)

  # CLI direct test:
  python kimi_client.py "Hello Kimi K3, explain your capabilities"
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# Automatically load environment variables from project .env
load_dotenv()

DEFAULT_MODAL_BASE_URL = os.getenv("KIMI_K3_BASE_URL", "https://api.moonshot.cn/v1")
DEFAULT_MODEL = "moonshotai/Kimi-K3"


def get_kimi_client() -> tuple[OpenAI, str]:
    """
    Initialize and return an OpenAI client configured for Kimi K3 (Modal or Moonshot).
    Returns (client, model_name).
    """
    # 1. Check for Modal Token ID & Secret
    token_id = os.getenv("MODAL_PROXY_TOKEN_ID", "").strip("'\" \t\r\n")
    token_secret = os.getenv("MODAL_PROXY_TOKEN_SECRET", "").strip("'\" \t\r\n")
    base_url = os.getenv("KIMI_K3_BASE_URL") or os.getenv("MOONSHOT_BASE_URL") or DEFAULT_MODAL_BASE_URL

    if token_id and token_secret:
        api_key = f"{token_id}.{token_secret}"
        model = os.getenv("KIMI_MODEL", DEFAULT_MODEL)
    else:
        # Fallback to direct MOONSHOT_API_KEY
        api_key = (os.getenv("MOONSHOT_API_KEY") or os.getenv("KIMI_API_KEY") or "").strip("'\" \t\r\n")
        model = os.getenv("MOONSHOT_MODEL", "moonshotai/Kimi-K3")

    if not api_key:
        raise ValueError(
            "Missing Kimi / Modal API credentials!\n"
            "Please check your .env file for MODAL_PROXY_TOKEN_ID and MODAL_PROXY_TOKEN_SECRET."
        )

    client = OpenAI(
        api_key=api_key,
        base_url=base_url.strip("'\" \t\r\n"),
    )
    return client, model


def ask_kimi(
    prompt: str,
    system_prompt: str = "You are a concise technical assistant.",
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
    top_p: float = 0.95,
    stream: bool = False,
):
    """
    Send a prompt to Kimi K3 and receive the response.
    """
    client, default_model_name = get_kimi_client()
    target_model = model or default_model_name

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model=target_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        stream=stream,
        extra_body={"reasoning_effort": "none"},
    )

    if stream:
        return response
    return response.choices[0].message.content


def main():
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Explain why low latency matters for LLM endpoints in three bullets."
    print(f"\n[Prompt]: {prompt}\n")
    try:
        client, model = get_kimi_client()
        print(f"[Connecting to Kimi K3 on {client.base_url} (Model: {model})...]")
        reply = ask_kimi(prompt)
        print(f"\n[Kimi K3 Response]:\n{reply}\n")
    except Exception as err:
        print(f"\n[Error]: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
