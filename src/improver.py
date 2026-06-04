import json
import os

IMPROVEMENTS_FILE = "src/improvements.json"

def load_improvements():
    if not os.path.exists(IMPROVEMENTS_FILE):
        return []
    with open(IMPROVEMENTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_improvement(suggestion):
    improvements = load_improvements()
    improvements.append({
        "suggestion": suggestion,
        "applied": True
    })
    with open(IMPROVEMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(improvements, f, indent=2)
    print("Yeti: Improvement saved! I'll apply it from next session.")

def get_improvements_summary():
    improvements = load_improvements()
    if not improvements:
        return "No improvements applied yet."
    return "\n".join(f"- {imp['suggestion']}" for imp in improvements)

def handle_suggestion(suggestion):
    print(f"\nYeti: I have a suggestion:\n  → {suggestion}")
    answer = input("Apply this improvement? (y/n): ").strip().lower()
    if answer == "y":
        save_improvement(suggestion)
        return True
    else:
        print("Yeti: Got it, skipping that one.")
        return False