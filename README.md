# Curious Bot

A tiny CLI chatbot that loads the persona from `bot_prompt.md` and chats via the OpenAI API.

## Setup

```bash
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4o-mini"  # optional
```

Optional env vars:

```bash
export BOT_PROMPT_PATH="bot_prompt.md"
export PROMO_CODES_PATH="promo_codes.json"
```

## Run

```bash
python3 bot.py
```

## Notes

- Edit `bot_prompt.md` to tweak the personality.
- Use `BOT_PROMPT_PATH` to point to a different prompt file.
- Type `promo` to show saved Mech Arena promo codes.
