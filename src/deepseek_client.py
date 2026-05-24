import os

from dotenv import load_dotenv
from openai import OpenAI


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"


def is_deepseek_configured() -> bool:
    load_dotenv()
    return bool(os.getenv("DEEPSEEK_API_KEY"))


def generate_ai_report(topic: str, pages: list[dict]) -> str:
    """Use DeepSeek to turn collected webpages into a Markdown report."""
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is missing. Please configure it in .env first.")

    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
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
