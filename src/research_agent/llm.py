import os
import json

from dotenv import load_dotenv
from openai import OpenAI


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_TIMEOUT = 20.0


def is_deepseek_configured() -> bool:
    load_dotenv()
    return bool(os.getenv("DEEPSEEK_API_KEY"))


def generate_ai_report(topic: str, pages: list[dict]) -> str:
    """Use DeepSeek to turn collected webpages into a Markdown report."""
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is missing. Please configure it in .env first.")

    client = build_client()
    model = os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a rigorous English-language research assistant. "
                    "Write the report only from the webpages provided by the user. "
                    "Do not invent sources. Output must be Markdown."
                ),
            },
            {
                "role": "user",
                "content": build_prompt(topic, pages),
            },
        ],
        temperature=0.2,
        max_tokens=1800,
        extra_body={"thinking": {"type": "disabled"}},
    )

    return response.choices[0].message.content.strip()


def chat_text(system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> str:
    """Call DeepSeek and return plain text."""
    client = build_client()
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=max_tokens,
        extra_body={"thinking": {"type": "disabled"}},
    )
    return response.choices[0].message.content.strip()


def chat_json(system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> dict:
    """Call DeepSeek and parse a JSON object from the response."""
    content = chat_text(system_prompt, user_prompt, max_tokens=max_tokens)
    return json.loads(strip_json_fence(content))


def generate_final_report_from_observations(task: str, observations: list[dict]) -> str:
    observation_text = "\n\n".join(
        [
            f"Step {item['step_id']} - {item['goal']} ({item['tool']}):\n{item['observation']}"
            for item in observations
        ]
    )
    return chat_text(
        system_prompt=(
            "You write clear Markdown reports from agent observations. "
            "Use only the provided observations. Do not invent facts."
        ),
        user_prompt=f"Task: {task}\n\nObservations:\n{observation_text[:16000]}",
        max_tokens=1800,
    )


def build_client() -> OpenAI:
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is missing. Please configure it in .env first.")

    timeout = float(os.getenv("DEEPSEEK_TIMEOUT", DEFAULT_TIMEOUT))
    return OpenAI(
        api_key=api_key,
        base_url=DEEPSEEK_BASE_URL,
        timeout=timeout,
        max_retries=0,
    )


def strip_json_fence(content: str) -> str:
    text = content.strip()
    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()
    elif text.startswith("```"):
        text = text.removeprefix("```").strip()

    if text.endswith("```"):
        text = text.removesuffix("```").strip()

    return text


def build_prompt(topic: str, pages: list[dict]) -> str:
    source_blocks = []

    for index, page in enumerate(pages, start=1):
        source_blocks.append(
            "\n".join(
                [
                    f"Source [{index}]",
                    f"Title: {page['title']}",
                    f"URL: {page['url']}",
                    "Text excerpt:",
                    page.get("text", "")[:5000],
                ]
            )
        )

    return "\n\n".join(
        [
            f"Research topic: {topic}",
            "Generate a clear English Markdown research report.",
            "Report structure:",
            "1. Title",
            "2. Executive Summary",
            "3. Key Findings",
            "4. Detailed Analysis",
            "5. Sources",
            "6. Follow-up Research Questions",
            "Requirements:",
            "- Make the key findings specific and concrete.",
            "- Use citation markers like [1] and [2] after factual claims.",
            "- List each source with its citation number, title, and URL.",
            "- Clearly state uncertainty when the provided material is insufficient.",
            "",
            "Webpage material:",
            "\n\n---\n\n".join(source_blocks),
        ]
    )
