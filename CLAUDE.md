# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Setup (using uv for venv)
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Run locally (debug mode on localhost:5000)
python app.py

# Docker build & run
docker build -t prompt-helper .
docker run -p 5000:5000 -e SECRET_KEY=your-secret prompt-helper
```

## Architecture

Flask app (single module) with SQLite database. No blueprints — all routes in `app.py`.

- `app.py` — App factory (`create_app()`), all routes, config, security headers, rate limiting
- `models.py` — SQLAlchemy models: `User` (auth) and `Prompt` (saved prompts)
- `forms.py` — WTForms: `SignupForm`, `LoginForm`, `PromptBuilderForm`
- `templates/` — Jinja2 templates extending `base.html`
- `static/` — Vanilla CSS + JS (live preview, copy-to-clipboard)

### Prompt Assembly

The `assemble_prompt()` function in `app.py` concatenates user inputs into the final prompt text. The assembled text is stored in the `prompts.assembled` column at save time — old prompts retain their original wording even if the template changes.

### Auth

Flask-Login session-based auth. Passwords hashed with werkzeug (scrypt). Every prompt route checks `prompt.user_id == current_user.id`.

### Security

CSRF via Flask-WTF, rate limiting via Flask-Limiter (5/min on auth routes), Jinja2 auto-escaping, security headers (`X-Content-Type-Options`, `X-Frame-Options`). `SECRET_KEY` from env var in production.

### Database

SQLite in `instance/prompt_helper.db`, auto-created on first run. Tables managed by `db.create_all()` — no migration tool configured.
