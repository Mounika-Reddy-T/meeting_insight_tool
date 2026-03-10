# Meeting Insight Tool

A document and meeting-transcript analyzer built with FastAPI, Streamlit, and OpenRouter.

## What It Does

The tool takes a long text input such as meeting notes or a transcript and extracts:

- Summary
- Action items
- Key decisions
- Risks
- Priority tasks
- Prompt and completion token counts

## Project Structure

```text
meeting_insight_tool/
  backend/
    api.py
    ai_engine.py
    schemas.py
  frontend/
    dashboard.py
  requirements.txt
  .env
```

## Requirements

- Python 3.10+
- An `OPENROUTER_API_KEY`

## Environment Variables

Add this to [`.env`](C:\Users\Ahex-Tech\Desktop\AI\meeting_insight_tool\.env):

```env
OPENROUTER_API_KEY=your_openrouter_api_key
```

## Install Dependencies

From the project folder:

```powershell
cd C:\Users\Ahex-Tech\Desktop\AI\meeting_insight_tool
pip install -r requirements.txt
```

## Run The Backend

From the backend folder:

```powershell
cd C:\Users\Ahex-Tech\Desktop\AI\meeting_insight_tool\backend
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

Backend docs:

```text
http://127.0.0.1:8000/docs
```

If `8000` is already taken, use another port such as `8001`. If you change the backend port, also update `API_ENDPOINT` in [dashboard.py](C:\Users\Ahex-Tech\Desktop\AI\meeting_insight_tool\frontend\dashboard.py).

## Run The Frontend

Open another terminal:

```powershell
cd C:\Users\Ahex-Tech\Desktop\AI\meeting_insight_tool\frontend
streamlit run dashboard.py
```

Streamlit will print the local URL in the terminal, usually:

```text
http://localhost:8501
```

## API Endpoint

### `POST /analyze-document`

Request body:

```json
{
  "text": "Project kickoff meeting notes..."
}
```

Response shape:

```json
{
  "summary": "string",
  "action_items": ["string"],
  "key_decisions": ["string"],
  "risks": ["string"],
  "priority_tasks": ["string"],
  "prompt_tokens": 0,
  "completion_tokens": 0
}
```

## Notes

- The FastAPI app lives in [api.py](C:\Users\Ahex-Tech\Desktop\AI\meeting_insight_tool\backend\api.py).
- OpenRouter request and parsing logic lives in [ai_engine.py](C:\Users\Ahex-Tech\Desktop\AI\meeting_insight_tool\backend\ai_engine.py).
- The Streamlit UI lives in [dashboard.py](C:\Users\Ahex-Tech\Desktop\AI\meeting_insight_tool\frontend\dashboard.py).
- Backend errors from OpenRouter are surfaced as HTTP `502`.

