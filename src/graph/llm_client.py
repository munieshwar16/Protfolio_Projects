"""
LLM Client (OpenAI API)
----------------------
Uses the OpenAI API for LLM inference. Requires OPENAI_API_KEY in environment.
This powers the Router, Clarifier, and Summarizer agents.
"""

import os
import openai
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")
openai.api_key = OPENAI_API_KEY

async def llm_call(prompt: str, system: str = None) -> str:
    """
    Run a prompt against the OpenAI API and return text output.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        max_tokens=128,
        temperature=0.2,
    )
    result = response.choices[0].message.content.strip()
    return result
