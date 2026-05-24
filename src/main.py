import sys

from deepseek_client import generate_ai_report, is_deepseek_configured
from extractor import extract_key_points, summarize_text
from fetcher import fetch_page_text
from reporter import save_ai_report, save_report
from search import search_web


def main() -> None:
    topic = parse_topic()
    print(f"调研任务：{topic}")

    print("1. 正在搜索网页...")
    try:
        search_results = search_web(topic, max_results=5)
    except Exception as error:
        print(f"搜索失败：{error}")
        print("请检查网络连接，或稍后重试。")
        return

    if not search_results:
        print("没有找到搜索结果，请换一个关键词重试。")
        return

    pages = []
    for index, result in enumerate(search_results, start=1):
        print(f"2.{index} 正在读取：{result['title']}")

        try:
            text = fetch_page_text(result["url"])
        except Exception as error:
            print(f"   跳过该网页，读取失败：{error}")
            continue

        if len(text) < 200:
            print("   跳过该网页，正文内容太少。")
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
        print("没有成功读取到可用网页内容，请稍后重试或更换调研任务。")
        return

    print("3. 正在生成 Markdown 报告...")

    if is_deepseek_configured():
        try:
            print("   已检测到 DeepSeek API Key，正在使用 AI 生成报告...")
            markdown = generate_ai_report(topic, pages)
            report_path = save_ai_report(topic, markdown)
        except Exception as error:
            print(f"   DeepSeek 生成失败，改用基础规则生成报告：{error}")
            report_path = save_report(topic, pages)
    else:
        print("   未配置 DeepSeek API Key，使用基础规则生成报告。")
        report_path = save_report(topic, pages)

    print(f"完成：{report_path}")


def parse_topic() -> str:
    if len(sys.argv) < 2:
        print('用法：python src/main.py "调研 apple 的 ai 战略"')
        raise SystemExit(1)

    return " ".join(sys.argv[1:]).strip()


if __name__ == "__main__":
    main()
