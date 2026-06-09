import subprocess
import webbrowser
import datetime
from src.commands.search import web_search

COMMAND_TRIGGERS = {
    "open chrome": ("Opening Chrome...", lambda: webbrowser.open("https://google.com")),
    "open youtube": ("Opening YouTube...", lambda: webbrowser.open("https://youtube.com")),
    "open github": ("Opening GitHub...", lambda: webbrowser.open("https://github.com/Krishal-Tha-Shrestha")),
    "open notepad": ("Opening Notepad...", lambda: subprocess.Popen("notepad.exe")),
    "open calculator": ("Opening Calculator...", lambda: subprocess.Popen("calc.exe")),
    "open vscode": ("Opening VS Code...", lambda: subprocess.Popen("code .", shell=True)),
    "shutdown": ("Shutting down in 10 seconds...", lambda: subprocess.Popen("shutdown /s /t 10")),
    "cancel shutdown": ("Shutdown cancelled.", lambda: subprocess.Popen("shutdown /a")),
}

def handle_command(user_input):
    lower = user_input.lower().strip()

    # Time and date — return directly
    if "what time is it" in lower:
        return f"It's {datetime.datetime.now().strftime('%I:%M %p')}"

    if "what's the date" in lower or "what is the date" in lower:
        return f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}"

    # Keyword commands
    for trigger, (message, action) in COMMAND_TRIGGERS.items():
        if trigger in lower:
            action()
            return message

    # Web search
    if lower.startswith("search for ") or lower.startswith("search "):
        query = lower.replace("search for ", "").replace("search ", "")
        raw, output = web_search(query)
        if raw:
            from src.ai import chat
            summary = chat(f"Based on these search results, give a brief summary:\n{raw}")
            return f"{output}\n\nYeti's take: {summary}"
        return output

    if lower.startswith("who is ") or lower.startswith("what is "):
        raw, output = web_search(lower)
        if raw:
            from src.ai import chat
            summary = chat(f"Based on these search results, give a brief summary:\n{raw}")
            return f"{output}\n\nYeti's take: {summary}"
        return output

    return None  # not a command