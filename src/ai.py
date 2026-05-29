import os
import datetime

LOG_FILE = "conversation_log.txt"

def save_to_log(role, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {role}: {message}\n")
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

LONG_TERM_MEMORY = """
Name: Krishal Tha Shrestha
Age: 18
Location: Bode, Madhyapur Thimi, Kathmandu, Nepal
Status: Completed Grade 12 (Science), awaiting results
Goal: BSc CSIT (college not decided yet)
Projects: Yeti AI Assistant (flagship, currently building v1),
          Python projects (rock paper scissors, guessing game, password generator),
          Face detection system (OpenCV),
          Web projects (portfolio, GPA calculator, task tracker)
Skills: Python (beginner), C, JavaScript, HTML/CSS, OpenCV, Linux (Ubuntu/Zorin), Git/GitHub
Learning style: Learns by doing, debugs himself first before asking,
                builds projects immediately after learning concepts
"""

SYSTEM_PROMPT = f"""You are Yeti, a personal AI assistant created by and for Krishal Tha Shrestha.
You are inspired by Jarvis from Iron Man.

── Permanent knowledge about your user ──
{LONG_TERM_MEMORY}

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

history = []

def chat(user_input):
    save_to_log("You", user_input)
    history.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        temperature=0.7,
        max_tokens=1024
    )

    reply = response.choices[0].message.content

    history.append({
        "role": "assistant",
        "content": reply
    })

    # Keep only last 10 messages (short-term window)
    if len(history) > 10:
        history.pop(0)
        history.pop(0)
    save_to_log("Yeti",reply)
    return reply