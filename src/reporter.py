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
        f"# 调研报告：{topic}",
        "",
        f"生成时间：{created_at}",
        "",
        "## 关键发现",
        "",
    ]

    key_points = []
    for page in pages:
        key_points.extend(page.get("key_points", []))

    if key_points:
        for point in key_points[:10]:
            lines.append(f"- {point}")
    else:
        lines.append("- 暂未提取到明确关键发现。")

    lines.extend(["", "## 信息来源", ""])
    for index, page in enumerate(pages, start=1):
        lines.append(f"{index}. [{page['title']}]({page['url']})")

    lines.extend(["", "## 网页摘要", ""])
    for index, page in enumerate(pages, start=1):
        lines.extend(
            [
                f"### {index}. {page['title']}",
                "",
                f"来源：{page['url']}",
                "",
                page.get("summary") or "未能生成摘要。",
                "",
            ]
        )

    lines.extend(
        [
            "## 后续可继续调研的问题",
            "",
            f"- {topic} 相关战略最近一年有哪些变化？",
            f"- {topic} 背后的核心产品、技术和合作伙伴是什么？",
            f"- {topic} 对行业竞争格局可能产生什么影响？",
            "",
        ]
    )

    return "\n".join(lines)


def build_filename(topic: str) -> str:
    safe_topic = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fa5]+", "-", topic).strip("-")
    safe_topic = safe_topic[:50] or "research"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{timestamp}-{safe_topic}.md"
