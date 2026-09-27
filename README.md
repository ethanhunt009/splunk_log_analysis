# AI Log Analysis & Suricata Rule Bot

## What it does
A chatbot that reads Splunk-style logs, finds problems, and writes Suricata rules — using an AI agent (Gemini or Claude) to pick the right tool for each request.

---

## Requirements
- Python 3.10+
- MongoDB running on `localhost:27017`
- Google API key (for Gemini)
- Anthropic API key (for Claude)

---

## Install

```
pip install langchain langchain-google-genai langchain-anthropic langchain-mongodb langchain-community pymongo python-dotenv
```

Create a `.env` file in the project folder with:

```
GOOGLE_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

---

## Run

```
python main.py
```

Type a request and press Enter. Type `exit` to quit.

---

## Files it uses

Reads:
- `normal_system_logs.csv` — the log file to load

Writes:
- `anomaly_report.txt` — anomaly reports
- `error_report.txt` — error reports
- `suricata_rules.txt` — generated Suricata rules

MongoDB:
- `LOG.LOGGING` — stores loaded log rows
- `chat.chat_history` — stores chat history

---

## Commands (just talk normally)

Load logs — say something like: `load the splunk logs`

Look at logs — say something like: `show me recent logs`

Search logs — say something like: `find failed logins`

Save an anomaly — say something like: `report this as an anomaly: <details>`

Save an error — say something like: `report this error: <details>`

Add a Suricata rule — say something like: `add suricata rule: drop ip 1.2.3.4 any -> any any (msg:"block"; sid:1; rev:1;)`

Quit — type: `exit`

---

## Suricata rule format

Must start with one of: `alert`, `drop`, `pass`, `reject`.

Example:

```
drop ip 10.0.0.5 any -> any any (msg:"Blocked brute-force"; sid:1000001; rev:1;)
```

Invalid rules are rejected.

---

## CSV format

Any CSV with a header row works. Each row becomes one MongoDB document.

To filter on specific columns, edit `read_splunk_logs()` in `agent.py` — by default it looks at `message` and `raw`.

---

## Config (edit in the code)

MongoDB URI — in both files — default `mongodb://localhost:27017`

Log DB and collection — in `agent.py` — default `LOG` and `LOGGING`

Chat DB and collection — in `main.py` — default `chat` and `chat_history`

Session ID — in `main.py` — default `session_1`

Gemini model — in `main.py` — default `gemini-2.0-flash`

Claude model — in `main.py` — default `claude-3-5-sonnet-20240620`

CSV path — in `agent.py` — default `normal_system_logs.csv`

---

## Troubleshooting

If it says `No log rows found`, say `load the splunk logs` first.

If it says `Invalid Suricata rule`, the rule must start with `alert`, `drop`, `pass`, or `reject`.

If MongoDB connection fails, make sure `mongod` is running.

If `GOOGLE_API_KEY not set` appears, check your `.env` file.

Duplicate rows won't happen — upsert skips identical rows.

---

## Notes
- The bot does not connect to a real Splunk server — it reads a local CSV.
- Always review generated Suricata rules before using them for real.
- Conversation memory is saved in MongoDB, so restarting keeps history.
