# AI Browser Agent

A beginner-friendly MVP: enter a research topic, search public webpages, read page content, extract basic information, and generate a Markdown research report.

## Current MVP Features

- Accept a research topic from the command line
- Search a configurable number of public webpages
- Fetch readable webpage text
- Use DeepSeek to generate a Markdown research report when an API key is configured
- Fall back to a simple rule-based report when no DeepSeek API key is configured
- Add numbered citations for sources
- Save generated reports to `reports/`

## Safety Boundaries

- No website login
- No form submission
- No payment, ordering, or other risky actions
- No bypassing website access restrictions

## Installation

Python 3.10 or later is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure DeepSeek

Copy the environment variable example file:

```bash
cp .env.example .env
```

Then open `.env` and add your own DeepSeek API key:

```text
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-v4-flash
```

`deepseek-v4-flash` is a good default for the beginner stage because it is faster and cheaper. For stronger output quality, change it to `deepseek-v4-pro`.

## Run

Start the program and enter your research topic when prompted:

```bash
python src/main.py
```

Example prompt:

```text
Enter research topic: research AI browsers
```

You can also pass the topic directly:

```bash
python src/main.py "research AI browser agents"
```

Control how many search results are fetched:

```bash
python src/main.py --max-results 3
```

After the command finishes, check the generated `.md` report in the `reports/` folder.

## Project Structure

```text
browser_agent/
├── README.md
├── requirements.txt
├── .env.example
├── reports/
│   └── .gitkeep
└── src/
    ├── main.py
    ├── search.py
    ├── fetcher.py
    ├── extractor.py
    ├── deepseek_client.py
    └── reporter.py
```

## Possible Next Steps

- Add webpage content deduplication
- Improve source filtering and ranking
- Add webpage content deduplication
- Add tests for the report generation logic
- Build a simple web UI
