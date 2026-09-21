"""
LLM Client Module
Handles communication with the AI model (Google Gemini).
Falls back to Demo Mode if no API key is configured.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("AI_API_KEY", "")
DEMO_MODE = not bool(API_KEY)

# Try to import Google GenAI
client = None
if not DEMO_MODE:
    try:
        from google import genai
        client = genai.Client(api_key=API_KEY)
    except ImportError:
        print("⚠️  google-genai not installed. Running in Demo Mode.")
        DEMO_MODE = True
    except Exception as e:
        print(f"⚠️  Failed to configure Gemini API: {e}. Running in Demo Mode.")
        DEMO_MODE = True


def call_llm(prompt: str) -> str:
    """
    Send a prompt to the LLM and return the response text.
    If no API key is set, returns a demo response.
    """
    if DEMO_MODE:
        return _demo_response(prompt)

    import time
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                time.sleep(2)  # Wait 2 seconds before retrying
                continue
            return f"[API Error] Could not get a response from the AI model: {e}"


def is_demo_mode() -> bool:
    """Check if the application is running in demo mode."""
    return DEMO_MODE


def _demo_response(prompt: str) -> str:
    """
    Generate a simple demo response based on keywords in the prompt.
    This is NOT real AI — it is a placeholder for demonstration purposes.
    """
    prompt_lower = prompt.lower()

    if "review" in prompt_lower:
        return (
            "## 🤖 Documentation Review (Demo Mode)\n\n"
            "**Status:** ✅ Documentation looks complete.\n\n"
            "**Checklist:**\n"
            "- ✅ All functions are documented.\n"
            "- ✅ Parameters are described.\n"
            "- ✅ Return values are explained.\n"
            "- ✅ Documentation matches the code structure.\n\n"
            "**Verdict:** The documentation is clear and consistent with the source code. "
            "No major issues found.\n\n"
            "> ⚠️ *This review was generated in Demo Mode (no AI API key configured).*"
        )

    # Default: generate documentation
    return (
        "# 📄 Code Documentation (Demo Mode)\n\n"
        "## Overview\n"
        "This module contains utility functions and/or classes as analyzed from the provided source code.\n\n"
        "## Functions\n\n"
        "### `main_function(param1, param2)`\n"
        "**Description:** Performs the primary operation of the module.\n\n"
        "**Parameters:**\n"
        "| Parameter | Type | Description |\n"
        "|-----------|------|-------------|\n"
        "| `param1` | varies | The first input value |\n"
        "| `param2` | varies | The second input value |\n\n"
        "**Returns:** The result of the operation.\n\n"
        "## Usage Example\n"
        "```python\n"
        "result = main_function(value1, value2)\n"
        "print(result)\n"
        "```\n\n"
        "> ⚠️ *This documentation was generated in Demo Mode (no AI API key configured). "
        "Connect an API key for real AI-generated documentation.*"
    )
