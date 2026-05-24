import re


def summarize_text(text: str, max_sentences: int = 4, max_chars: int = 900) -> str:
    """Create a simple extractive summary from the first useful sentences."""
    sentences = split_sentences(text)
    useful = [sentence for sentence in sentences if len(sentence) >= 40]
    summary_sentences = useful[:max_sentences]

    if not summary_sentences:
        return truncate(text, max_chars)

    return truncate(" ".join(summary_sentences), max_chars)


def extract_key_points(text: str, max_points: int = 5) -> list[str]:
    """Pick simple keyword-related sentences as key points."""
    keywords = [
        "ai",
        "artificial intelligence",
        "machine learning",
        "strategy",
        "model",
        "openai",
        "investment",
        "product",
        "privacy",
    ]
    sentences = split_sentences(text)
    points = []

    for sentence in sentences:
        lower = sentence.lower()
        if any(keyword in lower for keyword in keywords) and len(sentence) >= 50:
            points.append(truncate(sentence, 220))

        if len(points) >= max_points:
            break

    return points


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?。！？])\s+", text)
    return [part.strip() for part in parts if part.strip()]


def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text

    return text[:max_chars].rstrip() + "..."
