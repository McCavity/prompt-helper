# Prompt Helper

A lightweight web app that helps you craft structured AI prompts by answering four guided questions. Built with Flask, SQLite, and vanilla CSS/JS.

## Features

- **Guided prompt builder** — Answer four questions (expertise, task, context, constraints) and get a well-structured prompt with live preview
- **Prompt library** — Save, search, copy, and reuse your prompts
- **Edit as new** — Clone any saved prompt as a starting point for a new one
- **User accounts** — Signup/login with hashed passwords; each user sees only their own prompts
- **Multilingual** — English and German UI with language switcher on every page
- **Copy to clipboard** — One-click copy on both the builder preview and saved prompts

## Quick Start

### Local

```bash
# Create a virtual environment and install dependencies
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Run the app
python app.py
```

The app starts at **http://localhost:5000**.

### Docker

```bash
docker build -t prompt-helper .
docker run -p 5000:5000 -e SECRET_KEY=your-secret-here prompt-helper
```

## Changing the Port

Port 5000 is used by default. If it's already in use on your system (e.g. by AirPlay Receiver on macOS), change it as follows:

### Local

Pass the port via the `PORT` environment variable or edit the `app.run()` call in `app.py`:

```bash
# Option 1: environment variable
PORT=8080 python app.py

# Option 2: edit app.py directly
# Change: app.run(host="0.0.0.0", port=5000, debug=debug)
# To:     app.run(host="0.0.0.0", port=8080, debug=debug)
```

### Docker

Map a different host port while keeping the container port unchanged:

```bash
# Map host port 8080 to container port 5000
docker run -p 8080:5000 -e SECRET_KEY=your-secret-here prompt-helper
```

Or change both sides if you prefer the container to also use a different port:

```bash
docker run -p 8080:8080 -e PORT=8080 -e SECRET_KEY=your-secret-here prompt-helper
```

## Security

- CSRF protection on all forms (Flask-WTF)
- Passwords hashed with scrypt (werkzeug)
- Rate limiting on auth routes (Flask-Limiter)
- Security headers (X-Content-Type-Options, X-Frame-Options)
- Session cookies: HttpOnly, SameSite=Lax

## Tech Stack

- **Backend:** Python, Flask, SQLAlchemy, SQLite
- **Frontend:** Jinja2 templates, vanilla CSS, vanilla JS
- **Auth:** Flask-Login, werkzeug password hashing
