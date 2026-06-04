import subprocess
import webbrowser
import datetime

# Keywords that trigger commands instead of AI
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
    for trigger, action in COMMAND_TRIGGERS.items():
        if trigger in lower:
            action()
            return True
    return False