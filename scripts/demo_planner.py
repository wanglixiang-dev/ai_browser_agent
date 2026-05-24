import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from research_agent.agents.executor import execute_plan
from research_agent.agents.planner import create_plan


DEMO_TASK = "Open a webpage, summarize the main content, and generate a Markdown report."


def main() -> None:
    print(f"Demo task: {DEMO_TASK}")

    print("\n1. Planning")
    plan = create_plan(DEMO_TASK)
    print(json.dumps(plan.model_dump(), indent=2, ensure_ascii=False))

    print("\n2. Execution")
    result = execute_plan(plan, max_results=1)

    print("\n3. Status")
    for step in result.steps:
        print(f"- Step {step.step_id}: {step.status} ({step.tool})")
        if step.error:
            print(f"  Error: {step.error}")

    if result.final_report_path:
        print(f"\nFinal report: {result.final_report_path}")
    elif result.failed:
        print(f"\nExecution failed: {result.error}")


if __name__ == "__main__":
    main()
