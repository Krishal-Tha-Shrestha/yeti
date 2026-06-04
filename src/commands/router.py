import subprocess
import webbrowser
import datetime

from src.commands.search import web_search

COMMAND_TRIGGERS = {
    "open chrome": lambda: webbrowser.open("https://google.com"),
    "open youtube": lambda: webbrowser.open("https://youtube.com"),
    "open github": lambda: webbrowser.open("https://github.com/Krishal-Tha-Shrestha"),
    "what time is it": lambda: print(f"It's {datetime.datetime.now().strftime('%I:%M %p')}"),
    "what's the date": lambda: print(f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}"),
    "open notepad": lambda: subprocess.Popen("notepad.exe"),
    "open calculator": lambda: subprocess.Popen("calc.exe"),
    "shutdown": lambda: subprocess.Popen("shutdown /s /t 10"),
    "cancel shutdown": lambda: subprocess.Popen("shutdown /a"),
    "open vscode": lambda: subprocess.Popen("code .", shell=True),
}

def handle_command(user_input):
    lower = user_input.lower().strip()

    # Check keyword commands first
    for trigger, action in COMMAND_TRIGGERS.items():
        if trigger in lower:
            action()
            return True

    # Web search detection — outside the loop
    import subprocess
import webbrowser
import datetime

from src.commands.search import web_search

COMMAND_TRIGGERS = {
    "open chrome": lambda: webbrowser.open("https://google.com"),
    "open youtube": lambda: webbrowser.open("https://youtube.com"),
    "open github": lambda: webbrowser.open("https://github.com/Krishal-Tha-Shrestha"),
    "what time is it": lambda: print(f"It's {datetime.datetime.now().strftime('%I:%M %p')}"),
    "what's the date": lambda: print(f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}"),
    "open notepad": lambda: subprocess.Popen("notepad.exe"),
    "open calculator": lambda: subprocess.Popen("calc.exe"),
    "shutdown": lambda: subprocess.Popen("shutdown /s /t 10"),
    "cancel shutdown": lambda: subprocess.Popen("shutdown /a"),
    "open vscode": lambda: subprocess.Popen("code .", shell=True),
}

def handle_command(user_input):
    lower = user_input.lower().strip()

    # Check keyword commands first
    for trigger, action in COMMAND_TRIGGERS.items():
        if trigger in lower:
            action()
            return True

    # Web search detection — outside the loop
    if lower.startswith("search for ") or lower.startswith("search "):
        query = lower.replace("search for ", "").replace("search ", "")
        raw, output = web_search(query)
        print(output)
        if raw:
            from src.ai import chat
            summary = chat(f"Based on these search results, give a brief summary:\n{raw}")
            print(f"Yeti's take: {summary}")
        return True

    return False    
    return False