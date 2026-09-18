# Yeti — Personal AI Assistant

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-persistent%20memory-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

Yeti is a Jarvis-inspired personal AI assistant built with Python. It combines a FastAPI web server, a glassmorphism browser interface, persistent SQLite memory, and a dual AI brain that can use local Ollama models or fall back to Gemini in the cloud. Yeti is designed to become more useful and personalized over time while keeping the core application simple to run locally.

## Features

### Completed

#### v1 — Terminal assistant
- Interactive terminal chat through `src/main.py`.
- Graceful handling of quit commands, interrupts, timeouts, and connection errors.
- Conversation logging to `conversation_log.txt`.

#### v2 — Command router
- Natural-language routing for local commands.
- Quick actions such as opening applications and websites.
- Extensible command handling through `src/commands/router.py`.

#### v3 — Web interface
- FastAPI backend with a `/chat` endpoint.
- Responsive glassmorphism web UI.
- Chat bubbles, typing indicators, welcome prompts, quick commands, and web search support.
- DuckDuckGo-backed search with result summarization.
- Browser endpoints for serving the application and static assets.

#### v4 — Persistent memory and dual brain
- SQLite-backed conversation history in `yeti.db`.
- Persistent user profile facts stored in the `user_profile` table.
- Recent conversation context restored when Yeti starts.
- `remember that ...` support for saving new profile facts.
- Existing `conversation_log.txt` logging retained.
- Initial profile seeding with `scripts/seed_profile.py`.
- Ollama local brain using `qwen3:4b` when Ollama is available.
- Gemini cloud fallback using `GEMINI_API_KEY`.
- Runtime brain status and switching through `/status` and `/switch-brain`.
- Web UI brain switcher for local Ollama and cloud Gemini.

### Planned

#### v5 — Voice interaction ⏳
- Speech-to-text input.
- Text-to-speech responses.
- Optional wake-word activation.

#### v6 — Expanded integrations ⏳
- Calendar, reminders, and notifications.
- More system automation and desktop controls.
- Additional configurable skills and integrations.

#### v7 — Agent tools ⏳
- Safe file reading, writing, editing, listing, and searching.
- Controlled terminal command execution.
- AI tool-calling loop for multi-step tasks.
- Explicit confirmation for commands and destructive actions.
- Live tool-call progress in the web interface.

## Tech Stack

- **Backend:** Python + FastAPI
- **AI brain:** Ollama (local) with Gemini (cloud fallback)
- **Local model:** `qwen3:4b`
- **Memory:** SQLite persistent database
- **Frontend:** HTML/CSS/JavaScript glassmorphism web UI
- **Search:** DuckDuckGo via `ddgs`
- **Web scraping:** BeautifulSoup4-compatible scraping layer for planned and extended search workflows
- **Configuration:** `.env` loaded with `python-dotenv`

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/Krishal-Tha-Shrestha/yeti.git
cd yeti
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Install the repository dependencies first:

```bash
python -m pip install -r requirements.txt
```

For the FastAPI web server, dual-brain support, and search features, install any optional packages not already listed in your local requirements file:

```bash
python -m pip install fastapi uvicorn requests python-dotenv google-genai ddgs beautifulsoup4
```

### 4. Set up the `.env` file

Create a file named `.env` in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

`GEMINI_API_KEY` is used only when Gemini is selected or when Ollama is unavailable. Never commit `.env` or API keys to Git.

### 5. Start Ollama (optional but recommended)

Install Ollama from [ollama.com](https://ollama.com/), then start the service:

```bash
ollama serve
```

In another terminal, download the configured local model if needed:

```bash
ollama pull qwen3:4b
```

If Ollama is running at `http://localhost:11434`, Yeti selects it automatically at startup. Otherwise, Yeti uses Gemini as the cloud fallback.

### 6. Seed the initial profile

From the project root, run:

```bash
python scripts/seed_profile.py
```

This creates `yeti.db` and populates the initial user profile. The database is intentionally ignored by Git because it contains personal memory.

### 7. Run Yeti

#### Terminal mode

```bash
python src/main.py
```

#### Web mode

```bash
python server.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

The web interface provides:

- Chat with Yeti.
- Current brain and model status.
- Local Ollama / cloud Gemini switching.
- Quick commands and web search.
- Persistent conversation and profile memory.

## Project Structure

```text
yeti/
├── .env.example.txt          # Environment variable example
├── .gitignore                # Ignored files and local secrets
├── config.py                 # Application configuration placeholder
├── conversation_log.txt      # Human-readable conversation log
├── improvements.json         # Local improvement data
├── requirements.txt          # Python dependencies
├── server.py                 # FastAPI application and web endpoints
├── scripts/
│   └── seed_profile.py       # Seed initial SQLite profile facts
└── src/
    ├── ai.py                 # AI brains, chat flow, memory integration
    ├── improver.py           # Improvement data helpers
    ├── main.py               # Terminal application entry point
    ├── commands/
    │   ├── router.py         # Natural-language command routing
    │   └── search.py         # DuckDuckGo search integration
    ├── memory/
    │   └── database.py       # SQLite schema and persistence helpers
    └── static/
        └── index.html        # Glassmorphism web interface
```

Runtime-generated files:

```text
yeti.db                       # SQLite memory database; ignored by Git
conversation_log.txt          # Conversation log; local data
```

## Persistent Memory

Yeti stores two kinds of persistent data in SQLite:

- `chat_logs` — user and assistant messages, grouped by session.
- `user_profile` — durable facts such as name, goals, projects, skills, and new facts saved through `remember that ...`.

Example:

```text
remember that I am applying to Bhaktapur Multiple Campus
```

Profile data is local to the project by default. Back up `yeti.db` carefully because it may contain personal information.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Serves the web interface |
| `POST` | `/chat` | Sends a message to Yeti |
| `GET` | `/status` | Returns active brain, model, and Ollama availability |
| `POST` | `/switch-brain` | Switches between `ollama` and `gemini` |

Example brain switch request:

```json
{
  "brain": "ollama"
}
```

## Roadmap

| Version | Status | Focus |
| --- | --- | --- |
| v1 | ✅ Complete | Terminal assistant and conversation logging |
| v2 | ✅ Complete | Command routing and local actions |
| v3 | ✅ Complete | FastAPI server and glassmorphism web UI |
| v4 | ✅ Complete | SQLite persistent memory and dual AI brain |
| v5 | ⏳ Planned | Voice input, speech output, and wake-word support |
| v6 | ⏳ Planned | Calendar, reminders, notifications, and integrations |
| v7 | ⏳ Planned | Safe tool-calling agent capabilities |

## Safety and Privacy

- Keep API keys in `.env`, never in source code.
- Do not commit `yeti.db` or personal conversation logs.
- Review profile data before sharing database backups.
- Ollama keeps local model requests on your machine when the local brain is active.
- Gemini requests use the configured cloud API when Gemini is selected or used as fallback.

## Built by

**Krishal Tha Shrestha**

- GitHub: [Krishal-Tha-Shrestha](https://github.com/Krishal-Tha-Shrestha)
