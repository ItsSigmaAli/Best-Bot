#!/usr/bin/env python3
"""CLI chatbot with a curious, playful persona."""
from __future__ import annotations

import json
import os
import sys
import textwrap
import urllib.error
import urllib.request


DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
API_URL = os.environ.get("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
PROMPT_PATH = os.environ.get("BOT_PROMPT_PATH", "bot_prompt.md")
PROMO_CODES_PATH = os.environ.get("PROMO_CODES_PATH", "promo_codes.json")


def load_persona_prompt(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as prompt_file:
            return prompt_file.read().strip()
    except FileNotFoundError:
        return "You are a curious, playful assistant who learns by doing and joking."


def load_promo_codes(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as promo_file:
            return json.load(promo_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"game": "Mech Arena", "last_updated": "unknown", "codes": []}


def format_promo_codes(payload: dict) -> str:
    codes = payload.get("codes", [])
    if not codes:
        return (
            "I don't have any saved Mech Arena promo codes yet. "
            "Add them to promo_codes.json and try again."
        )
    lines = [
        f"Mech Arena promo codes (last updated {payload.get('last_updated', 'unknown')}):"
    ]
    lines.extend(f"- {code}" for code in codes)
    return "\n".join(lines)


def call_openai(messages: list[dict[str, str]], model: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY in environment.")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"API error {exc.code}: {body}") from exc

    return data["choices"][0]["message"]["content"].strip()


def format_assistant_message(text: str) -> str:
    return textwrap.fill(text, width=88)


def main() -> int:
    persona = load_persona_prompt(PROMPT_PATH)
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": persona,
        }
    ]

    print("Curious Bot ready. Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nLater! ✌️")
            return 0

        if user_input.lower() in {"exit", "quit"}:
            print("Later! ✌️")
            return 0

        if not user_input:
            print("Bot: Give me something to poke at. 😄")
            continue

        if user_input.lower() in {"promo", "promos", "promo codes", "promocodes"}:
            promo_payload = load_promo_codes(PROMO_CODES_PATH)
            print(f"Bot: {format_promo_codes(promo_payload)}\n")
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            reply = call_openai(messages, DEFAULT_MODEL)
        except RuntimeError as exc:
            print(f"Bot: {exc}")
            print("Bot: Add your OPENAI_API_KEY and try again.")
            return 1

        messages.append({"role": "assistant", "content": reply})
        print(f"Bot: {format_assistant_message(reply)}\n")


if __name__ == "__main__":
    sys.exit(main())
