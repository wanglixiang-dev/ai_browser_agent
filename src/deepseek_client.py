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
        raise RuntimeError("缺少 DEEPSEEK_API_KEY，请先在 .env 中配置。")

    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
    model = os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个严谨的中文研究助手。"
                    "请只基于用户提供的网页资料写报告，不要编造来源。"
                    "输出必须是 Markdown。"
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
                    f"资料 {index}",
                    f"标题：{page['title']}",
                    f"链接：{page['url']}",
                    "正文节选：",
                    page.get("text", "")[:5000],
                ]
            )
        )

    return "\n\n".join(
        [
            f"调研主题：{topic}",
            "请生成一份结构清晰的中文 Markdown 调研报告。",
            "报告结构：",
            "1. 标题",
            "2. 执行摘要",
            "3. 关键发现",
            "4. 详细分析",
            "5. 信息来源",
            "6. 后续可继续调研的问题",
            "要求：",
            "- 关键发现要具体，不要空泛。",
            "- 信息来源必须列出标题和链接。",
            "- 如果资料不足，要明确说明不确定性。",
            "",
            "网页资料：",
            "\n\n---\n\n".join(source_blocks),
        ]
    )
