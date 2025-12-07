# 🎙️ LiveKit Intelligent Interruption Handler  
### Enhancing Real-Time Conversational Flow in AI Voice Agents

🔗 **Demonstration Video:** *https://drive.google.com/file/d/1h9DUsZpNI-5waWcUFdSCM2hUE1ObmL8G/view?usp=sharing*

---

## 📌 Project Overview

This project implements an **Intelligent Interruption Handling Layer** on top of the LiveKit Agent Framework.  
The objective is to solve the issue where **passive acknowledgements** like “yeah”, “ok”, “hmm”, “uh-huh” incorrectly interrupt the agent while it's speaking.

Using the logic requirements defined in the assignment brief, this implementation ensures:

- When **agent is speaking** → ignore “yeah/ok/hmm/right/uh-huh”
- When **agent is silent** → respond normally
- If user says **interruptive commands** (“stop”, “wait”, “no”) → agent stops immediately
- Mixed sentences like **“yeah wait a sec”** → interruption is triggered correctly  
- **No modification to VAD** — the logic sits above VAD

Your full implementation lives inside:

MY_INTERRUPT_AGENT/

---

## ✨ Features Implemented

### ✅ 1. Configurable Ignore List
Soft acknowledgements that should be ignored while the agent is speaking:
['yeah', 'ok', 'okay', 'hmm', 'right', 'uh-huh', 'uh huh']

csharp


### ✅ 2. Speaking-State-Aware Filtering
- If agent is speaking → soft words are ignored  
- If agent is silent → soft words become valid inputs  

### ✅ 3. Mixed Command Handling
Presence of a real command:
["stop", "wait", "no", "hold on"]

→ triggers interruption immediately.

### ✅ 4. Zero-Latency User Experience
The agent does not pause, glitch, or stutter.

---

# 📂 Repository Structure

agents-assignment/
│
├── MY_INTERRUPT_AGENT/
│ ├── agent.py
│ ├── README.md
│ ├── requirements.txt
│
└── other assignment folders


---

# 🚀 How to Run This Project (MY_INTERRUPT_AGENT)

## 1️⃣ Clone the repository
```bash
git clone https://github.com/saharsh3008/agents-assignment.git
cd agents-assignment/MY_INTERRUPT_AGENT
```
## 2️⃣ Create virtual environment
```bash
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```
## 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```
## 4️⃣ Add your environment variables
Create a .env file:
```bash
ini
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
GROQ_API_KEY=your_key
CARTESIA_API_KEY=your_key
DEEPGRAM_API_KEY=your_key
```
## 5️⃣ Run the Agent
```bash
python agent.py dev
```

# 🧪 Test Scenarios Demonstrated
✔ Scenario 1 — Soft words ignored while agent is talking
✔ Scenario 2 — “Yeah” is processed normally when agent is silent
✔ Scenario 3 — “Stop/Wait/No” interrupt immediately
✔ Scenario 4 — Mixed inputs like “yeah but wait” trigger interruption

# 🛠️ How It Works (Summary)
Inside agent.py:

Tracks agent speaking state

Processes STT before deciding to interrupt

Filters passive words

Detects interruptive commands

Ensures uninterrupted smooth audio output

The logic ensures no stutter, no pauses, no hiccups — exactly as required.

# 📜 Submission Checklist
✔ New branch: interrupt-handler-saharsh
✔ Folder: MY_INTERRUPT_AGENT
✔ Working agent logic
✔ README added
✔ Video demonstration (add link at top)
