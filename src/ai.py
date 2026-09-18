import os
import datetime
import re
import sys

LOG_FILE = "conversation_log.txt"

def save_to_log(role, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {role}: {message}\n")

import requests
from dotenv import load_dotenv

load_dotenv()

# Determine which brain to use: Ollama (local) or Gemini (cloud)
BRAIN = None
OLLAMA_URL = "http://localhost:11434"
OLLAMA_API_CHAT = OLLAMA_URL + "/api/chat"  # best-effort endpoint; may vary by Ollama version
OLLAMA_MODEL = "qwen3:4b"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gpt-4o-mini")

try:
    r = requests.get(OLLAMA_URL, timeout=1)
    ollama_available = (r.status_code == 200)
except Exception:
    ollama_available = False

if ollama_available:
    BRAIN = "ollama"
    print("🧠 Brain: Ollama (local)")
else:
    BRAIN = "gemini"
    print("🧠 Brain: Gemini (cloud)")

# Public active brain variable (can be switched at runtime)
ACTIVE_BRAIN = BRAIN

# If Gemini is selected at startup, initialize google-genai client (lazy init also supported)
client_gemini = None
if ACTIVE_BRAIN == "gemini":
    try:
        from google import genai
        client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    except Exception:
        client_gemini = None
        # Leave it to the chat call to initialize lazily or raise a helpful error


def get_status():
    """Return a status dict for the web UI: active brain, model, and whether Ollama is reachable."""
    try:
        r = requests.get(OLLAMA_URL, timeout=1)
        ollama_up = (r.status_code == 200)
    except Exception:
        ollama_up = False
    model = OLLAMA_MODEL if ACTIVE_BRAIN == "ollama" else GEMINI_MODEL
    return {"brain": ACTIVE_BRAIN, "model": model, "ollama_available": ollama_up}


def set_active_brain(brain: str):
    """Attempt to switch the ACTIVE_BRAIN. Returns True if switched, False otherwise."""
    global ACTIVE_BRAIN, client_gemini
    brain = brain.lower()
    if brain == "ollama":
        # Verify Ollama is reachable
        try:
            r = requests.get(OLLAMA_URL, timeout=1)
            if r.status_code == 200:
                ACTIVE_BRAIN = "ollama"
                return True
            else:
                return False
        except Exception:
            return False
    elif brain == "gemini":
        # Initialize gemini client lazily if needed
        if client_gemini is None:
            try:
                from google import genai
                client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            except Exception:
                client_gemini = None
                # cannot initialize gemini
                return False
        ACTIVE_BRAIN = "gemini"
        return True
    else:
        return False


# Import the database module located in src/memory by adding that folder to sys.path
DB_MODULE_PATH = os.path.join(os.path.dirname(__file__), "memory")
if DB_MODULE_PATH not in sys.path:
    sys.path.insert(0, DB_MODULE_PATH)
import database as db

# Ensure DB is initialized
db.init_db()

def build_system_prompt():
    """Build the SYSTEM_PROMPT dynamically from profile facts in the DB."""
    long_term_memory = db.get_all_profile_facts()
    return f"""You are Yeti, a personal AI assistant created by and for Krishal Tha Shrestha.
You are inspired by Jarvis from Iron Man.

── Permanent knowledge about your user ──
{long_term_memory}

── How you behave ──
- Call the user Krishal
- Be casual and friendly by default
- Switch to precise and technical when helping with code
- Keep responses short and punchy unless deep explanation is needed
- When helping with code, always explain WHY not just what
- You have a slight personality — not robotic, not overly casual
- Before responding, think briefly about what Krishal actually needs
  Format your thinking as: [Thinking: your brief thought here]
  Keep thinking to 1-2 sentences max, directly relevant to the question
- After thinking, give your actual response normally
- Never be verbose or repeat yourself
- Never use asterisk actions like *checks logs* or *simulation error*
- Never roleplay physical actions, just respond directly
"""

# Use SQLite-backed short-term history loaded from DB
history = db.get_recent_messages(20)

# session id groups messages from the same run; use ISO datetime
SESSION_ID = datetime.datetime.now().isoformat()


def chat(user_input):
    """Main chat entry point. Loads system prompt and recent history from DB,
    sends to model, saves both user and assistant messages to DB, and
    handles "remember that" style facts.
    """
    global ACTIVE_BRAIN
    # Work with a local copy of the active brain so runtime switching is possible
    brain = ACTIVE_BRAIN
    # Always log to conversation_log.txt
    save_to_log("You", user_input)

    # Save user message to DB
    db.save_message(SESSION_ID, "user", user_input)

    # Detect "remember that" and save profile facts if present
    m = re.search(r"remember that\b", user_input, flags=re.IGNORECASE)
    if m:
        fact_text = user_input[m.end():].strip()
        # Try to parse "my KEY is VALUE" patterns
        kv = re.search(r"(?i)^(?:my\s+)?(?P<key>\w[\w\s-]{0,50}?)\s*(?:is|=|:)\s*(?P<value>.+)$", fact_text.strip())
        if kv:
            key = kv.group('key').strip().lower().replace(' ', '_')
            value = kv.group('value').strip()
            db.save_profile_fact(key, value)
            ack = f"Okay, remembered {key}: {value}"
            save_to_log("Yeti", ack)
            db.save_message(SESSION_ID, "assistant", ack)
            return ack
        else:
            # Generic note entry
            note_key = f"note:{datetime.datetime.now().isoformat()}"
            db.save_profile_fact(note_key, fact_text)
            ack = "Okay, I've remembered that."
            save_to_log("Yeti", ack)
            db.save_message(SESSION_ID, "assistant", ack)
            return ack

    # Build messages: dynamic system prompt + recent history
    system_prompt = build_system_prompt()
    messages = [{"role": "system", "content": system_prompt}] + history

    # Send to the selected brain (Ollama local HTTP or Gemini via google-genai)
    reply = None

    if brain == "ollama":
        try:
            payload = {"model": OLLAMA_MODEL, "messages": messages}
            r = requests.post(OLLAMA_API_CHAT, json=payload, timeout=30)
            r.raise_for_status()
            j = r.json()
            # Try common response shapes
            if isinstance(j, dict):
                if "choices" in j and j["choices"]:
                    # OpenAI-like shape
                    try:
                        reply = j["choices"][0]["message"]["content"]
                    except Exception:
                        reply = j["choices"][0].get("text") or str(j["choices"][0])
                elif "text" in j:
                    reply = j["text"]
                elif "response" in j:
                    reply = j["response"]
                else:
                    reply = str(j)
            else:
                reply = str(j)
        except Exception as e:
            # If Ollama call fails, switch to Gemini fallback
            print("⚠️ Ollama call failed, switching to Gemini (cloud):", str(e))
            brain = "gemini"
            ACTIVE_BRAIN = "gemini"

    if brain == "gemini":
        # Ensure a gemini client is available (initialize lazily if Ollama was chosen at startup)
        gemini_client = client_gemini
        if gemini_client is None:
            try:
                from google import genai
                gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            except Exception:
                raise RuntimeError("Gemini client not initialized. Set GEMINI_API_KEY in environment and install google-genai.")
        # Try several common client interfaces for google-genai
        try:
            # Preferred: gemini_client.chat.completions.create (OpenAI-like wrapper)
            if hasattr(gemini_client, "chat") and hasattr(gemini_client.chat, "completions"):
                response = gemini_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7,
                    max_output_tokens=1024
                )
                # Attempt to extract content
                try:
                    reply = response.choices[0].message.content
                except Exception:
                    reply = getattr(response, "content", None) or str(response)
            # Fallback: gemini_client.generate_text or gemini_client.generate
            elif hasattr(gemini_client, "generate_text"):
                # Build a plain prompt combining system + recent messages
                prompt_body = system_prompt + "\n\n" + "\n".join([f"{m['role']}: {m['content']}" for m in messages if m['role'] != 'system'])
                gen = gemini_client.generate_text(model="gpt-4o-mini", input=prompt_body)
                reply = getattr(gen, "text", None) or str(gen)
            elif hasattr(gemini_client, "generate"):
                gen = gemini_client.generate(model="gpt-4o-mini", prompt=system_prompt)
                reply = str(gen)
            else:
                raise RuntimeError("Unsupported google-genai client interface")
        except Exception as e:
            raise RuntimeError(f"Gemini request failed: {e}")

    if reply is None:
        raise RuntimeError("No reply generated from any brain")

    # Save assistant reply to DB and log files
    db.save_message(SESSION_ID, "assistant", reply)
    save_to_log("Yeti", reply)

    # Update in-memory short history window
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": reply})
    # keep only the last 20 items (10 exchanges)
    if len(history) > 20:
        history = history[-20:]

    return reply
