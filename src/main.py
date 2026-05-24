import argparse

from deepseek_client import generate_ai_report, is_deepseek_configured
from extractor import extract_key_points, summarize_text
from fetcher import fetch_page_text
from reporter import save_ai_report, save_report
from search import search_web


def main() -> None:
    args = parse_args()
    topic = args.topic
    print(f"Research topic: {topic}")
    print(f"Max search results: {args.max_results}")

    print("1. Searching webpages...")
    try:
        search_results = search_web(topic, max_results=args.max_results)
    except Exception as error:
        print(f"Search failed: {error}")
        print("Please check your network connection or try again later.")
        return

    if not search_results:
        print("No search results found. Please try another keyword.")
        return

    pages = []
    for index, result in enumerate(search_results, start=1):
        print(f"2.{index} Reading: {result['title']}")

        try:
            text = fetch_page_text(result["url"])
        except Exception as error:
            print(f"   Skipped. Failed to read webpage: {error}")
            continue

        if len(text) < 200:
            print("   Skipped. The webpage text is too short.")
            continue

        pages.append(
            {
                "title": result["title"],
                "url": result["url"],
                "text": text,
                "summary": summarize_text(text),
                "key_points": extract_key_points(text),
            }
        )

    if not pages:
        print("No usable webpage content was fetched. Please try again later or use another topic.")
        return

    print("3. Generating Markdown report...")

    if is_deepseek_configured():
        try:
            print("   DeepSeek API key detected. Generating an AI report...")
            markdown = generate_ai_report(topic, pages)
            report_path = save_ai_report(topic, markdown)
        except Exception as error:
            print(f"   DeepSeek generation failed. Falling back to the rule-based report: {error}")
            report_path = save_report(topic, pages)
    else:
        print("   DeepSeek API key is not configured. Using the rule-based report.")
        report_path = save_report(topic, pages)

    print(f"Done: {report_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search public webpages and generate a Markdown research report."
    )
    parser.add_argument("topic", help="Research topic, for example: research Apple's AI strategy")
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum number of search results to fetch. Default: 5. Range: 1-10.",
    )

    args = parser.parse_args()

    if args.max_results < 1 or args.max_results > 10:
        parser.error("--max-results must be between 1 and 10.")

    return args


if __name__ == "__main__":
    main()
