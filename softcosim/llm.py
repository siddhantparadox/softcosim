import os
import aiohttp
import time

API_URL = "https://openrouter.ai/api/v1/chat/completions"

async def chat(model: str, messages: list[dict], stream: bool = False) -> tuple[str, float, float]:
    """
    Returns (response_text, usd_cost, latency_s)
    If SOFTCOSIM_FAKE_LLM=1 → returns canned text, zero cost.
    """
    if os.getenv("SOFTCOSIM_FAKE_LLM") == "1":
        return "FAKE-LLM-REPLY", 0.0, 0.0

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    body = {
        "model": model,
        "messages": messages,
        "usage": {"include": True},
        "stream": stream
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    t0 = time.perf_counter()
    async with aiohttp.ClientSession() as s:
        async with s.post(API_URL, headers=headers, json=body) as r:
            if not stream:
                data = await r.json()
                usage = data.get("usage", {})
                # OpenRouter cost is in credits, 1/1000 of a cent.
                # We want USD.
                cost = usage.get("cost", 0.0)
                latency = time.perf_counter() - t0
                return data["choices"][0]["message"]["content"], cost, latency
            else:
                # Streaming logic to be implemented later
                return "STREAMING-NOT-IMPLEMENTED", 0.0, 0.0
