# J.A.R.V.I.S. — Live Voice AI Assistant

A modular, Windows-oriented personal voice assistant built with Python and the Google Gemini Live API.

## Project status

This repository documents the source code as uploaded. The assistant currently requires a valid Gemini API key and an account/project with working API billing and quota. If billing or quota is unavailable, the live AI connection will not work even though the local Python source remains available.

The project was previously developed as a live voice-assistant prototype. Do not interpret this repository as a guarantee that the current API account or model access is active.

## Features implemented in the source

- Continuous microphone audio capture and streaming to the Gemini Live API.
- Audio response playback through the system speaker.
- Function/tool calling through a separate tool registry and executor.
- Windows application, folder, file, window, clipboard and system utility tools.
- Google Search grounding configured in the Live API session.
- Session resumption and context-window compression configuration.
- Screen capture support through the vision module.
- Timers, reminders and a local memory utility.

Some tools can make changes to the local computer, including file operations and terminal commands. Review the code and use these capabilities carefully.

## Project structure

```text
JARVIS/
├── main.py
├── live_test.py
├── config.py
├── tools.py
├── tool_registry.py
├── tool_executor.py
├── clipboard.py
└── vision.py
```

## Requirements

- Windows 10/11
- Python 3.11+ recommended (the original project was developed in a newer Python environment; audio-device compatibility may vary)
- A working microphone and speaker
- A Google AI Studio / Gemini API key with access to the configured Live API model and available billing/quota

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Configure the API key

The application reads the `GEMINI_API_KEY` environment variable. It does not require an API key to be written into the source code.

In PowerShell, set it for the current terminal session:

```powershell
$env:GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Then start the assistant:

```powershell
python main.py
```

To store the variable persistently for your Windows user account, use Windows Environment Variables settings. Restart the terminal after changing a persistent environment variable.

Never commit API keys, `.env` files, personal credentials, or private account information to GitHub.

## Troubleshooting

- **Billing / quota errors:** Check the Google AI project linked to the API key, billing status, API limits and model availability. A billing restriction is an account/API-access issue and may prevent the Live API connection.
- **`GEMINI_API_KEY is not set`:** Set the environment variable in the same terminal session from which you run `python main.py`.
- **Microphone / speaker errors:** Check Windows microphone permissions, the selected input/output devices and `sounddevice` compatibility.
- **Dependency errors:** Reinstall the packages listed in `requirements.txt` in the Python environment used to run the project.

## Security

- Keep API keys private. If a key has ever been committed to a public repository or shared publicly, revoke it and create a replacement.
- This assistant has tools that can interact with files, applications, windows, clipboard contents and terminal commands. Read `tools.py` and `tool_registry.py` before running it.
- Do not run untrusted commands or grant access to sensitive files.

## Author

Munagapaka Rakesh Kumar  
Diploma in Electronics and Communication Engineering
