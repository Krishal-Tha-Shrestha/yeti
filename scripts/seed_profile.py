import os
import sys

# Add src/memory to path so we can import database module
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MEMORY_PATH = os.path.join(PROJECT_ROOT, 'src', 'memory')
if MEMORY_PATH not in sys.path:
    sys.path.insert(0, MEMORY_PATH)

import database

# Initialize DB and seed profile facts

def seed():
    database.init_db()
    profile = {
        'name': 'Krishal Tha Shrestha',
        'age': '18',
        'location': 'Bode, Madhyapur Thimi, Kathmandu, Nepal',
        'status': 'Completed Grade 12, NEB GPA 2.74, checking college eligibility',
        'goal': 'BSc CSIT or BIT/BCA',
        'hardware': 'Acer Nitro V15 RTX 4050, HP G42 planned server',
        'skills': 'Python, C, JavaScript, HTML/CSS, OpenCV, Linux, Git/GitHub',
        'learning_style': 'Learns by doing, debugs himself first',
        'projects': 'Yeti AI Assistant, Python projects, Face detection, Discord bot, Portfolio'
    }

    for k, v in profile.items():
        database.save_profile_fact(k, v)
    print('Seeded profile facts into yeti.db')

if __name__ == '__main__':
    seed()
