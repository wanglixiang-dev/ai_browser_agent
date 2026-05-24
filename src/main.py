import argparse
import json

from agents.executor import execute_plan
from agents.planner import create_plan


def main() -> None:
    args = parse_args()
    topic = args.topic
    print(f"User task: {topic}")
    print(f"Max search results: {args.max_results}")
    if args.resume_file:
        print(f"Resume file: {args.resume_file}")
    if args.resume_output:
        print(f"Resume output: {args.resume_output}")

    print("\n1. Creating task plan...")
    plan = create_plan(topic)
    print(json.dumps(plan.model_dump(), indent=2, ensure_ascii=False))

    print("\n2. Executing task plan...")
    result = execute_plan(
        plan,
        max_results=args.max_results,
        resume_file=args.resume_file,
        resume_output=args.resume_output,
    )

    print("\n3. Execution summary...")
    for step in result.steps:
        print(f"- Step {step.step_id}: {step.status} ({step.tool})")
        if step.error:
            print(f"  Error: {step.error}")

    if result.final_report_path:
        print(f"\nFinal report: {result.final_report_path}")
        if result.context.get("resume_output_path"):
            print(f"Resume draft: {result.context['resume_output_path']}")
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
    parser.add_argument(
        "--resume-file",
        help="Optional local resume file path. Supported formats: .txt, .md, .markdown.",
    )
    parser.add_argument(
        "--resume-output",
        help="Optional output path for a rewritten resume draft. Does not overwrite the original resume.",
    )

    args = parser.parse_args()

    if args.max_results < 1 or args.max_results > 10:
        parser.error("--max-results must be between 1 and 10.")

    if not args.topic:
        args.topic = input("Enter research topic: ").strip()

    if not args.topic:
        parser.error("research topic cannot be empty.")

    return args


if __name__ == "__main__":
    main()
