import os
import aiohttp
import asyncio
import time
import json
from typing import AsyncIterator

API_URL = "https://openrouter.ai/api/v1/chat/completions"

async def chat(model: str, messages: list[dict], stream: bool = False):
    """Talks to the OpenRouter API.

    Parameters
    ----------
    model : str
        The model name to query.
    messages : list[dict]
        OpenAI style chat messages.
    stream : bool, optional
        When ``True`` an async iterator of tokens is returned. Otherwise the
        full reply text, cost and latency are returned.

    Returns
    -------
    tuple[str, float, float] | AsyncIterator[str]
        Non-streaming returns ``(response_text, usd_cost, latency_s)`` while
        streaming returns an async iterator yielding tokens.

    Notes
    -----
    If ``SOFTCOSIM_FAKE_LLM=1`` the reply is faked and costs/latency are zero.
    """
    if os.getenv("SOFTCOSIM_FAKE_LLM") == "1":
        if stream:
            async def fake_gen():
                yield "FAKE-LLM-REPLY"
            return fake_gen()
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
                async def gen() -> AsyncIterator[str]:
                    cost = 0.0
                    try:
                        async for chunk in r.content:
                            text = chunk.decode("utf-8").strip()
                            if not text:
                                continue
                            for line in text.splitlines():
                                if line.startswith("data:"):
                                    line = line[5:].strip()
                                if not line:
                                    continue
                                if line == "[DONE]":
                                    return
                                try:
                                    payload = json.loads(line)
                                except json.JSONDecodeError:
                                    continue
                                delta = payload.get("choices", [{}])[0].get("delta", {})
                                token = delta.get("content")
                                if token:
                                    yield token
                                usage = payload.get("usage")
                                if usage:
                                    cost = usage.get("cost", cost)
                    finally:
                        gen.latency = time.perf_counter() - t0
                        gen.cost = cost

                gen.cost = 0.0
                gen.latency = 0.0
                return gen()
