from typing import Any, Callable
from pathlib import Path

from deepseek_client import (
    chat_text,
    generate_final_report_from_observations,
    generate_resume_draft,
    is_deepseek_configured,
)
from fetcher import fetch_page_text
from reporter import save_ai_report
from search import search_web


ToolFunction = Callable[[Any, dict], Any]


def search_web_tool(tool_input: Any, context: dict) -> list[dict]:
    query = str(tool_input or context["task"])
    return search_web(query, max_results=context.get("max_results", 3))


def browser_open_tool(tool_input: Any, context: dict) -> dict:
    url = resolve_url(tool_input, context)
    text = fetch_page_text(url)
    return {"url": url, "text": text[:12000]}


def llm_extract_tool(tool_input: Any, context: dict) -> str | dict:
    content = stringify(tool_input)
    resume_context = build_resume_context(context)
    if not is_deepseek_configured():
        return (content + resume_context)[:1200]

    return chat_text(
        system_prompt="Extract structured information from the provided material. Be concise.",
        user_prompt=f"Task: {context['task']}\n\nMaterial:\n{content[:12000]}{resume_context}",
        max_tokens=1000,
    )


def llm_analyze_tool(tool_input: Any, context: dict) -> str:
    content = stringify(tool_input)
    resume_context = build_resume_context(context)
    if not is_deepseek_configured():
        return f"Rule-based analysis fallback:\n\n{(content + resume_context)[:1200]}"

    return chat_text(
        system_prompt=(
            "Analyze the provided information for the user's task. "
            "If resume text is provided, compare it with the target role or webpage content "
            "and give concrete resume improvement suggestions. Be practical and specific. "
            "Do not claim the user already has skills or experience that are not in the resume. "
            "Separate truthful rewrites from recommended additions."
        ),
        user_prompt=f"Task: {context['task']}\n\nInformation:\n{content[:12000]}{resume_context}",
        max_tokens=1400,
    )


def report_write_tool(tool_input: Any, context: dict) -> str:
    observations = list(context["observations"])
    if context.get("resume_text"):
        observations.append(
            {
                "step_id": "resume",
                "goal": "User resume context",
                "tool": "resume.context",
                "observation": context["resume_text"][:8000],
            }
        )

    if is_deepseek_configured():
        markdown = generate_final_report_from_observations(context["task"], observations)
    else:
        markdown = build_fallback_report(context["task"], observations)

    report_path = save_ai_report(context["task"], markdown)
    context["final_report_path"] = str(report_path)
    context["final_answer"] = markdown

    if context.get("resume_output") and context.get("resume_text"):
        resume_output_path = write_resume_draft(context, observations)
        context["resume_output_path"] = str(resume_output_path)

    return str(report_path)


TOOLS: dict[str, ToolFunction] = {
    "search.web": search_web_tool,
    "browser.open": browser_open_tool,
    "llm.extract": llm_extract_tool,
    "llm.analyze": llm_analyze_tool,
    "report.write": report_write_tool,
}


def get_tool(tool_name: str) -> ToolFunction:
    if tool_name not in TOOLS:
        available = ", ".join(sorted(TOOLS))
        raise ValueError(f"Unknown tool '{tool_name}'. Available tools: {available}")
    return TOOLS[tool_name]


def resolve_url(tool_input: Any, context: dict) -> str:
    if isinstance(tool_input, str) and tool_input.startswith(("http://", "https://")):
        return tool_input

    if isinstance(tool_input, dict) and tool_input.get("url"):
        return str(tool_input["url"])

    if isinstance(tool_input, list) and tool_input:
        first = tool_input[0]
        if isinstance(first, dict) and first.get("url"):
            return str(first["url"])

    for observation in reversed(context["observations"]):
        value = observation.get("observation")
        if isinstance(value, list) and value:
            first = value[0]
            if isinstance(first, dict) and first.get("url"):
                return str(first["url"])

    raise ValueError("browser.open needs a URL or a previous search result with a URL.")


def stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    return repr(value)


def build_fallback_report(task: str, observations: list[dict]) -> str:
    lines = [f"# Task Report: {task}", "", "## Observations", ""]
    for item in observations:
        lines.extend(
            [
                f"### Step {item['step_id']}: {item['goal']}",
                "",
                stringify(item["observation"])[:1500],
                "",
            ]
        )
    return "\n".join(lines)


def build_resume_context(context: dict) -> str:
    resume_text = context.get("resume_text")
    if not resume_text:
        return ""

    return f"\n\nResume text:\n{resume_text[:8000]}"


def write_resume_draft(context: dict, observations: list[dict]) -> Path:
    output_path = Path(context["resume_output"]).expanduser().resolve()
    original_path = Path(context["resume_file"]).expanduser().resolve()

    if output_path == original_path:
        raise ValueError("resume output path must be different from the original resume file.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if is_deepseek_configured():
        markdown = generate_resume_draft(context["task"], context["resume_text"], observations)
    else:
        markdown = context["resume_text"]

    output_path.write_text(markdown + "\n", encoding="utf-8")
    return output_path
