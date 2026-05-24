from typing import Any, Callable

from research_agent.browser import fetch_page_text
from research_agent.llm import chat_text, generate_final_report_from_observations, is_deepseek_configured
from research_agent.reports import save_ai_report
from research_agent.search import search_web


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
    if not is_deepseek_configured():
        return content[:1200]

    return chat_text(
        system_prompt="Extract structured information from the provided material. Be concise.",
        user_prompt=f"Task: {context['task']}\n\nMaterial:\n{content[:12000]}",
        max_tokens=1000,
    )


def llm_analyze_tool(tool_input: Any, context: dict) -> str:
    content = stringify(tool_input)
    if not is_deepseek_configured():
        return f"Rule-based analysis fallback:\n\n{content[:1200]}"

    return chat_text(
        system_prompt="Analyze the provided information for the user's task. Be practical and specific.",
        user_prompt=f"Task: {context['task']}\n\nInformation:\n{content[:12000]}",
        max_tokens=1400,
    )


def report_write_tool(tool_input: Any, context: dict) -> str:
    if is_deepseek_configured():
        markdown = generate_final_report_from_observations(context["task"], context["observations"])
    else:
        markdown = build_fallback_report(context["task"], context["observations"])

    report_path = save_ai_report(context["task"], markdown)
    context["final_report_path"] = str(report_path)
    context["final_answer"] = markdown
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
