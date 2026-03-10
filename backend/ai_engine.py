import json
import os
import re

import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _clean_list_item(line: str) -> str:
    item = line.strip()
    item = re.sub(r"^[\-\*\u2022]\s*", "", item)
    item = re.sub(r"^\d+[\.\)]\s*", "", item)
    return item.strip(" :")


def _extract_section_items(message: str, heading: str) -> list[str]:
    pattern = (
        rf"(?is){heading}\s*:?\s*(.+?)"
        r"(?=\n\s*(Summary|Action Items|Key Decisions|Risks|Priority Tasks)\s*:?\s*|\Z)"
    )
    match = re.search(pattern, message)
    if not match:
        return []

    section = match.group(1).strip()
    items = []
    for line in section.splitlines():
        line = line.strip()
        if not line:
            continue
        cleaned = _clean_list_item(line)
        if cleaned and cleaned.lower() not in {"none", "n/a"}:
            items.append(cleaned)

    return items


def _extract_summary(message: str) -> str:
    pattern = (
        r"(?is)Summary\s*:?\s*(.+?)"
        r"(?=\n\s*(Action Items|Key Decisions|Risks|Priority Tasks)\s*:?\s*|\Z)"
    )
    match = re.search(pattern, message)
    if match:
        return match.group(1).strip()
    return message.strip()


def _parse_model_output(message: str) -> dict:
    cleaned = _strip_code_fences(message)
    try:
        parsed = json.loads(cleaned)
        return {
            "summary": str(parsed.get("summary", "")).strip(),
            "action_items": [str(x).strip() for x in parsed.get("action_items", []) if str(x).strip()],
            "key_decisions": [str(x).strip() for x in parsed.get("key_decisions", []) if str(x).strip()],
            "risks": [str(x).strip() for x in parsed.get("risks", []) if str(x).strip()],
            "priority_tasks": [str(x).strip() for x in parsed.get("priority_tasks", []) if str(x).strip()],
        }
    except json.JSONDecodeError:
        return {
            "summary": _extract_summary(cleaned),
            "action_items": _extract_section_items(cleaned, "Action Items"),
            "key_decisions": _extract_section_items(cleaned, "Key Decisions"),
            "risks": _extract_section_items(cleaned, "Risks"),
            "priority_tasks": _extract_section_items(cleaned, "Priority Tasks"),
        }


async def generate_insights(text: str):
    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured. Add it to your environment or .env file."
        )

    payload = {
        "model": "openai/gpt-4o-mini",
        "temperature": 0.3,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You analyze documents and extract summary, action items, key decisions, risks, and priority tasks. "
                    "Return only valid JSON with exactly these keys: "
                    "summary (string), action_items (array of strings), key_decisions (array of strings), "
                    "risks (array of strings), priority_tasks (array of strings). "
                    "Do not include markdown or extra text."
                ),
            },
            {"role": "user", "content": text},
        ],
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "meeting-insight-tool",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)

    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"OpenRouter returned a non-JSON response (status {response.status_code})."
        ) from exc

    if response.status_code >= 400:
        error_message = data.get("error", {}).get("message", "Unknown OpenRouter error")
        raise RuntimeError(f"OpenRouter error ({response.status_code}): {error_message}")

    if "choices" not in data:
        raise RuntimeError("Invalid response from OpenRouter: missing choices")

    message = data["choices"][0]["message"]["content"]
    parsed = _parse_model_output(message)

    usage = data.get("usage", {})

    return {
        "summary": parsed.get("summary", ""),
        "action_items": parsed.get("action_items", []),
        "key_decisions": parsed.get("key_decisions", []),
        "risks": parsed.get("risks", []),
        "priority_tasks": parsed.get("priority_tasks", []),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
    }
