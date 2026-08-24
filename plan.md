# Overview
A command-line tool to send personalized bulk emails via SendGrid using a local SQLite database for contact lists, templates, and send history. The user manages recipients and templates via CLI commands, then triggers a send run that processes the queue sequentially with basic rate limiting and retry logic. Designed for a single operator sending up to ~10k emails/month from a local machine or simple VPS.

# Recommended Stack
- **Language**: Python 3.11+ — excellent stdlib, email libraries, and CLI tooling.
- **CLI Framework**: Typer — modern, type-hint driven, minimal boilerplate.
- **ESP**: SendGrid (Free Tier: 100 emails/day) — reliable API, simple auth, good Python SDK.
- **Storage**: SQLite (via `sqlite3` stdlib) — zero-config, file-based, perfect for solo/small data.
- **Templating**: Jinja2 — powerful, sandboxed, standard for Python.
- **HTTP Client**: `httpx` — modern async/sync client, used by SendGrid SDK internally.
- **Config**: `python-dotenv` — loads `.env` for API keys.

# Project Structure
```
bulk_emailer/
├── .env                  # SENDGRID_API_KEY, FROM_EMAIL, FROM_NAME
├── main.py               # Typer CLI entrypoint (commands: init, add-contact, send, status)
├── db.py                 # SQLite connection, schema init, CRUD helpers
├── models.py             # Dataclasses for Contact, Template, Campaign, SendLog
├── sender.py             # SendGrid wrapper: build payload, send, handle rate limits/retries
├── templates/
│   └── welcome.html.j2   # Example Jinja2 template
└── requirements.txt      # Pinned dependencies
```

# Proposed Components
| File / Function | Purpose |
| :--- | :--- |
| `main.py: app` | Typer CLI app instance. |
| `main.py: init_db()` | Creates `contacts`, `templates`, `campaigns`, `send_log` tables. |
| `main.py: add_contact()` | Upserts email, name, custom fields (JSON), tags into `contacts`. |
| `main.py: create_template()` | Stores template name, subject, HTML/Text body in `templates`. |
| `main.py: create_campaign()` | Links template + contact filter (tags/sql) + send config (rate limit) in `campaigns`. |
| `main.py: send_campaign()` | Main loop: fetches contacts, renders template per contact, calls `sender.send()`, logs result, sleeps for rate limit. |
| `main.py: status()` | Shows campaign stats: sent, failed, pending counts from `send_log`. |
| `db.py: get_conn()` | Returns singleton SQLite connection with `row_factory=sqlite3.Row`. |
| `db.py: execute()` / `query()` | Thin wrappers for parameterized SQL execution. |
| `sender.py: send_email()` | Builds SendGrid `Mail` object, calls API with exponential backoff (max 3 retries), returns `(success, error_msg)`. |
| `sender.py: rate_limiter()` | Generator yielding delay based on `emails_per_second` config. |

# Execution Plan
1.  Initialize project: `mkdir bulk_emailer && cd bulk_emailer && python -m venv .venv && source .venv/bin/activate`.
2.  Create `requirements.txt` with `typer[all]`, `sendgrid`, `jinja2`, `python-dotenv`, `httpx`; run `pip install -r requirements.txt`.
3.  Write `db.py` with schema: `contacts(id, email, name, data_json, tags)`, `templates(id, name, subject, html_body, text_body)`, `campaigns(id, name, template_id, filter_sql, rate_limit)`, `send_log(id, campaign_id, contact_id, status, error, sent_at)`.
4.  Write `models.py` dataclasses matching tables.
5.  Write `sender.py` using `sendgrid.helpers.mail.Mail` and `sendgrid.SendGridAPIClient`; implement retry logic for 429/5xx.
6.  Write `main.py` wiring Typer commands to DB and Sender; implement Jinja2 rendering with `autoescape=True`.
7.  Add example template `templates/welcome.html.j2` with `{{ name }}` and `{{ custom_field }}` placeholders.
8.  Create `.env.example` documenting required vars; user copies to `.env` and adds SendGrid API key.

# Verification Plan
- `python main.py init-db` → confirms `emailer.db` created with 4 tables.
- `python main.py add-contact --email "test@example.com" --name "Test User" --tags "welcome"` → contact appears in `sqlite3 emailer.db "SELECT * FROM contacts;"`.
- `python main.py create-template --name "welcome" --subject "Hello {{ name }}" --html-file templates/welcome.html.j2` → template stored.
- `python main.py create-campaign --name "welcome-run" --template welcome --filter "tags LIKE '%welcome%'" --rate-limit 1` → campaign created.
- `python main.py send-campaign --name "welcome-run"` → runs send loop; check console for "Sent to test@example.com" or error.
- Check `sqlite3 emailer.db "SELECT * FROM send_log;"` → shows one row with `status='sent'` and valid `sent_at` timestamp.

# Open Questions
No open questions.