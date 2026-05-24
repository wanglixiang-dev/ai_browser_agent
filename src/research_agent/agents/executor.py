from research_agent.agents.models import ExecutionResult, TaskPlan
from research_agent.tools.registry import get_tool


def execute_plan(plan: TaskPlan, max_results: int = 3) -> ExecutionResult:
    """Run plan steps one by one and store each observation or error."""
    context = {"task": plan.task, "observations": [], "max_results": max_results}

    for step in plan.steps:
        step.status = "running"
        print(f"Running step {step.step_id}: {step.goal} ({step.tool})")

        try:
            tool_fn = get_tool(step.tool)
            step_input = resolve_step_input(step.input, context)
            observation = tool_fn(step_input, context)
            step.observation = observation
            step.status = "completed"
            context["observations"].append(
                {
                    "step_id": step.step_id,
                    "goal": step.goal,
                    "tool": step.tool,
                    "observation": observation,
                }
            )
            print(f"Completed step {step.step_id}")
        except Exception as error:
            step.status = "failed"
            step.error = str(error)
            print(f"Failed step {step.step_id}: {error}")
            return ExecutionResult(
                task=plan.task,
                steps=plan.steps,
                failed=True,
                error=str(error),
                context=context,
            )

    return ExecutionResult(
        task=plan.task,
        steps=plan.steps,
        final_report_path=context.get("final_report_path"),
        final_answer=context.get("final_answer"),
        context=context,
    )


def resolve_step_input(step_input: str | dict | None, context: dict):
    if step_input == "previous_observation":
        if not context["observations"]:
            return None
        return context["observations"][-1]["observation"]

    return step_input
