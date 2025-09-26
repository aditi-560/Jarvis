## Jarvis Voice Agent (Gemini + STT/TTS)

### Setup

1. Create and activate a virtual environment (recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with:
   ```bash
   GEMINI_API_KEY=your_api_key_here
   ```

### Run

```bash
python jarvis.py
```

Say "Jarvis" before your command. Examples:
- "Jarvis open YouTube"
- "Jarvis what's the time"
- "Jarvis shutdown" (requires voice confirmation)

### Notes

- Requires microphone access. On Windows, install `PyAudio` wheels if needed.
- The assistant ignores speech without the wake word.
- Destructive actions require confirmation.


