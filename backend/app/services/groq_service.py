"""
Groq AI Service — wraps the Groq Python SDK.
All AI calls go through this service.
"""
from groq import Groq
from app.core.config import settings

_client: Groq | None = None


def get_groq_client() -> Groq:
    global _client
    if _client is None:
        key = settings.groq_api_key
        if key:
            # Mask the key for logging: "gsk_...3ImFvf"
            masked = key[:7] + "..." + key[-6:] if len(key) > 13 else "SHORT_KEY"
            print(f"DEBUG: Groq API Key loaded: {masked}")
        else:
            print("ERROR: Groq API Key is EMPTY!")
        _client = Groq(api_key=key)
    return _client


def chat_completion(
    messages: list[dict],
    system: str = "",
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    """
    Send a chat completion request to Groq.
    Returns the assistant reply as a plain string.
    """
    client = get_groq_client()
    full_messages = []

    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    response = client.chat.completions.create(
        model=model or settings.groq_model,
        messages=full_messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content


def json_completion(
    prompt: str,
    system: str = "",
    model: str | None = None,
    max_tokens: int = 2048,
) -> str:
    """
    Request a JSON-only response from Groq.
    Returns raw string — caller must parse JSON.
    """
    json_system = (system + "\n\n" if system else "") + \
        "IMPORTANT: Respond ONLY with valid JSON. No markdown, no explanation, no backticks."

    return chat_completion(
        messages=[{"role": "user", "content": prompt}],
        system=json_system,
        model=model,
        max_tokens=max_tokens,
        temperature=0.3,
    )
