from datetime import datetime
from pathlib import Path
import re


REPORTS_DIR = Path("reports")


def save_report(topic: str, pages: list[dict]) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)

    filename = build_filename(topic)
    report_path = REPORTS_DIR / filename
    report_path.write_text(build_markdown(topic, pages), encoding="utf-8")

    return report_path


def save_ai_report(topic: str, markdown: str) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)

    filename = build_filename(topic)
    report_path = REPORTS_DIR / filename
    report_path.write_text(markdown + "\n", encoding="utf-8")

    return report_path


def build_markdown(topic: str, pages: list[dict]) -> str:
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Research Report: {topic}",
        "",
        f"Generated at: {created_at}",
        "",
        "## Key Findings",
        "",
    ]

    key_points = []
    for page in pages:
        key_points.extend(page.get("key_points", []))

    if key_points:
        for point in key_points[:10]:
            lines.append(f"- {point}")
    else:
        lines.append("- No clear key findings were extracted.")

    lines.extend(["", "## Sources", ""])
    for index, page in enumerate(pages, start=1):
        lines.append(f"{index}. [{page['title']}]({page['url']})")

    lines.extend(["", "## Webpage Summaries", ""])
    for index, page in enumerate(pages, start=1):
        lines.extend(
            [
                f"### {index}. {page['title']}",
                "",
                f"Source: {page['url']}",
                "",
                page.get("summary") or "No summary was generated.",
                "",
            ]
        )

    lines.extend(
        [
            "## Follow-up Research Questions",
            "",
            f"- How has the strategy related to {topic} changed over the past year?",
            f"- What are the core products, technologies, and partners behind {topic}?",
            f"- What impact could {topic} have on the competitive landscape?",
            "",
        ]
    )

    return "\n".join(lines)


def build_filename(topic: str) -> str:
    safe_topic = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fa5]+", "-", topic).strip("-")
    safe_topic = safe_topic[:50] or "research"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{timestamp}-{safe_topic}.md"
