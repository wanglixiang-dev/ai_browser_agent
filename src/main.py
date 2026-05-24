import sys

from deepseek_client import generate_ai_report, is_deepseek_configured
from extractor import extract_key_points, summarize_text
from fetcher import fetch_page_text
from reporter import save_ai_report, save_report
from search import search_web


def main() -> None:
    topic = parse_topic()
    print(f"Research topic: {topic}")

    print("1. Searching webpages...")
    try:
        search_results = search_web(topic, max_results=5)
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


def parse_topic() -> str:
    if len(sys.argv) < 2:
        print('Usage: python src/main.py "research Apple\'s AI strategy"')
        raise SystemExit(1)

    return " ".join(sys.argv[1:]).strip()


if __name__ == "__main__":
    main()
