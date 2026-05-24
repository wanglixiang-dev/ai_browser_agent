# AI Browser Agent

一个适合新手学习的最小可行版本：用户输入调研主题，程序自动搜索公开网页，读取网页内容，提取基础信息，并生成 Markdown 调研报告。

## 当前 MVP 能力

- 接收一个调研任务
- 搜索 3-5 个公开网页
- 抓取网页正文
- 如果配置了 DeepSeek API Key，使用 DeepSeek 生成 Markdown 调研报告
- 如果没有配置 DeepSeek API Key，自动退回基础规则摘要
- 生成 Markdown 报告到 `reports/`

## 不做的事情

- 不登录网站
- 不提交表单
- 不支付、下单或执行危险操作
- 不绕过网站权限限制

## 安装

建议使用 Python 3.10 或更高版本。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 配置 DeepSeek

复制环境变量示例文件：

```bash
cp .env.example .env
```

然后打开 `.env`，填入你自己的 DeepSeek API Key：

```text
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-v4-flash
```

`deepseek-v4-flash` 更适合新手阶段，速度快、成本低。如果后续想要更强效果，可以改成 `deepseek-v4-pro`。

## 运行

```bash
python src/main.py "调研 apple 的 ai 战略"
```

运行完成后，在 `reports/` 文件夹里查看生成的 `.md` 报告。

## 项目结构

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

## 下一阶段可以做什么

- 增加网页内容去重
- 增加引用编号
- 支持指定搜索结果数量
- 支持更多搜索结果
- 做一个简单网页界面
