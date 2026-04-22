import httpx
import asyncio
import json
import logging
import time
from typing import AsyncGenerator, Optional

logger = logging.getLogger(__name__)

# Import config values 
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

# ────────────────────────────────────────────
# SYNCHRONOUS — use inside agents (run in thread pool by FastAPI)
# ────────────────────────────────────────────

def call_ollama_sync(
    system_prompt: str,
    user_prompt: str,
    model: str = None,
    max_tokens: int = 800,
    temperature: float = 0.3,
    max_retries: int = 3,
) -> Optional[str]:
    model = model or OLLAMA_MODEL
    payload = {
        "model":  model,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
        }
    }
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=OLLAMA_TIMEOUT) as client:
                response = client.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                result = data.get("response", "").strip()
                if result:
                    return result
                return None
        except httpx.TimeoutException:
            logger.warning(
                f"Ollama timeout on attempt {attempt+1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
        except httpx.ConnectError:
            logger.error("Ollama not reachable at " + OLLAMA_BASE_URL)
            return None
        except Exception as e:
            logger.error(f"Ollama error attempt {attempt+1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return None

# Keep backwards compatibility — old code calls call_ollama()
def call_ollama(
    model: str,
    system_prompt: str,
    user_prompt: str,
    timeout: int = None,
    max_retries: int = 3,
    max_tokens: int = 800,
    temperature: float = 0.3,
) -> Optional[str]:
    return call_ollama_sync(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        max_retries=max_retries,
    )

# ────────────────────────────────────────────
# ASYNC STREAMING — use in FastAPI chat endpoint
# ────────────────────────────────────────────

async def stream_ollama(
    system_prompt: str,
    user_prompt: str,
    model: str = None,
    max_tokens: int = 300,
    temperature: float = 0.3,
) -> AsyncGenerator[str, None]:
    model = model or OLLAMA_MODEL
    payload = {
        "model":  model,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": True,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
        }
    }
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(OLLAMA_TIMEOUT)
        ) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        if chunk.get("done"):
                            break
                        text = chunk.get("response", "")
                        if text:
                            yield text
                    except json.JSONDecodeError:
                        continue
    except httpx.ConnectError:
        logger.error("Ollama not reachable for streaming")
        yield "Ollama is not running. Please start Ollama and try again."
    except httpx.TimeoutException:
        logger.error("Ollama streaming timeout")
        yield "Response timed out."
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield "Analysis unavailable. Please try again."

# ────────────────────────────────────────────
# ASYNC NON-STREAMING — use when you need await but not streaming
# ────────────────────────────────────────────

async def call_ollama_async(
    system_prompt: str,
    user_prompt: str,
    model: str = None,
    max_tokens: int = 800,
    temperature: float = 0.3,
) -> Optional[str]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: call_ollama_sync(
            system_prompt, user_prompt,
            model, max_tokens, temperature
        )
    )

# ────────────────────────────────────────────
# HEALTH CHECK
# ────────────────────────────────────────────

async def check_ollama_health() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return r.status_code == 200
    except Exception:
        return False
