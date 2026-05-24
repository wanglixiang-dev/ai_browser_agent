from pathlib import Path

from agents.models import PlanStep, TaskPlan
from deepseek_client import chat_json, is_deepseek_configured


PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "planner_prompt.txt"


def create_plan(user_task: str) -> TaskPlan:
    """Create a structured task plan with DeepSeek, falling back to a simple plan."""
    if not is_deepseek_configured():
        return create_fallback_plan(user_task)

    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    try:
        data = chat_json(
            system_prompt=prompt,
            user_prompt=f"User task: {user_task}",
            max_tokens=1400,
        )
        plan = TaskPlan.model_validate(data)
        return normalize_plan(plan, user_task)
    except Exception:
        return create_fallback_plan(user_task)


def normalize_plan(plan: TaskPlan, user_task: str) -> TaskPlan:
    plan.task = plan.task or user_task
    for index, step in enumerate(plan.steps, start=1):
        step.step_id = index
        step.status = "pending"
        step.observation = None
        step.error = None
    return plan


def create_fallback_plan(user_task: str) -> TaskPlan:
    """Fallback plan keeps the agent usable when the LLM planner is unavailable."""
    url = extract_url(user_task)
    if url:
        opening_steps = [
            PlanStep(
                step_id=1,
                goal="Open the user-provided webpage",
                tool="browser.open",
                input=url,
                expected_output="Readable webpage text",
            )
        ]
    else:
        opening_steps = [
            PlanStep(
                step_id=1,
                goal="Search for relevant public webpages",
                tool="search.web",
                input=user_task,
                expected_output="A short list of relevant webpage results",
            ),
            PlanStep(
                step_id=2,
                goal="Open the most relevant search result",
                tool="browser.open",
                input="previous_observation",
                expected_output="Readable webpage text",
            ),
        ]

    start_id = len(opening_steps) + 1
    steps = opening_steps + [
        PlanStep(
            step_id=start_id,
            goal="Extract the most important information",
            tool="llm.extract",
            input="previous_observation",
            expected_output="Structured key information",
        ),
        PlanStep(
            step_id=start_id + 1,
            goal="Analyze the extracted information for the user task",
            tool="llm.analyze",
            input="previous_observation",
            expected_output="Analysis and recommendations",
        ),
        PlanStep(
            step_id=start_id + 2,
            goal="Write the final Markdown report",
            tool="report.write",
            input="previous_observation",
            expected_output="Markdown report file path",
        ),
    ]
    return TaskPlan(task=user_task, steps=steps)


def extract_url(text: str) -> str | None:
    for part in text.split():
        if part.startswith("http://") or part.startswith("https://"):
            return part.rstrip(".,)")
    return None
