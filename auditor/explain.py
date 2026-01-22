import json
import os
from typing import Any, Dict
from urllib import request, error
from dotenv import load_dotenv

load_dotenv()

def explain_report(report: dict) -> str:
    prompt = f"""
You are a senior ML engineer.

Explain the following data audit results to a junior data scientist.
Be concrete. Avoid buzzwords.

Audit Report:
{json.dumps(report, indent=2)}

Explain what data drift means,
why the detected features are risky,
and what actions an ML engineer should take next
(e.g., retraining, feature review, alerting).
"""

    # Replace with your LLM call
    # response = llm_client(prompt)
    # return response
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL")
    if not api_key or not model:
        return "LLM explanation placeholder."

    payload: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
    }

    req = request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
        data = json.loads(body)
        return data["choices"][0]["message"]["content"]
    except (error.URLError, KeyError, IndexError, json.JSONDecodeError):
        return "LLM explanation placeholder."
