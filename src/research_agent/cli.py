import argparse
import json
import sys

from research_agent.agents.executor import execute_plan
from research_agent.agents.planner import create_plan


def main() -> None:
    enable_line_buffering()
    args = parse_args()
    topic = args.topic
    print(f"User task: {topic}")
    print(f"Max search results: {args.max_results}")

    print("\n1. Creating task plan...")
    plan = create_plan(topic)
    print(json.dumps(plan.model_dump(), indent=2, ensure_ascii=False))

    print("\n2. Executing task plan...")
    result = execute_plan(plan, max_results=args.max_results)

    print("\n3. Execution summary...")
    for step in result.steps:
        print(f"- Step {step.step_id}: {step.status} ({step.tool})")
        if step.error:
            print(f"  Error: {step.error}")

    if result.final_report_path:
        print(f"\nFinal report: {result.final_report_path}")
    elif result.failed:
        print(f"\nExecution failed: {result.error}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search public webpages and generate a Markdown research report."
    )
    parser.add_argument(
        "topic",
        nargs="?",
        help="Optional research topic. If omitted, the program will ask for it.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum number of search results to fetch. Default: 5. Range: 1-10.",
    )

    args = parser.parse_args()

    if args.max_results < 1 or args.max_results > 10:
        parser.error("--max-results must be between 1 and 10.")

    if not args.topic:
        args.topic = input("Enter research topic: ").strip()

    if not args.topic:
        parser.error("research topic cannot be empty.")

    return args


def enable_line_buffering() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
