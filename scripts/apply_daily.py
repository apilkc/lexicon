#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
SCHEDULE = ROOT / "data" / "daily_schedule.json"
WORD_BANK = ROOT / "data" / "word_bank.json"
TIMEZONE = "America/Detroit"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def pick_day(schedule: list[dict]) -> dict:
    today = datetime.now(ZoneInfo(TIMEZONE)).date().isoformat()
    by_date = {item["date"]: item for item in schedule}
    if today in by_date:
        return by_date[today]

    ordered = sorted(schedule, key=lambda x: x["date"])
    earlier = [item for item in ordered if item["date"] <= today]
    return earlier[-1] if earlier else ordered[0]


def html_escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def highlight_words(passage: str, words: list[str]) -> str:
    escaped = html_escape(passage)
    for word in sorted(words, key=len, reverse=True):
        pattern = re.compile(rf"(?<![\w-])({re.escape(html_escape(word))})(?![\w-])", re.I)
        escaped = pattern.sub(
            lambda m: f'<span class="vocab" data-word="{html_escape(word)}">{m.group(1)}</span>',
            escaped,
        )
    return escaped


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Could not update {label}; expected one match, found {count}.")
    return new_text


def main() -> None:
    schedule = load_json(SCHEDULE)
    word_bank = load_json(WORD_BANK)
    day = pick_day(schedule)

    html = INDEX.read_text(encoding="utf-8")

    bank_js = json.dumps(word_bank, ensure_ascii=False, separators=(",", ":"))
    html = replace_once(
        html,
        r"const words=\[.*?\];\s*const state=",
        f"const words={bank_js};\nconst state=",
        "word bank",
    )

    passage_html = highlight_words(day["passage"], day["words"])
    article = (
        '<article class="card">'
        f'<div class="eyebrow">Daily Reading · {html_escape(day["difficulty"])} · {day["minutes"]} min</div>'
        f'<h2 class="title">{html_escape(day["title"])}</h2>'
        f'<div class="small">{html_escape(day["category"])} · {html_escape(day["date"])}</div>'
        f'<div class="passage">{passage_html}</div>'
        f'<p class="small">{html_escape(day["source_note"])}</p>'
        '</article>'
    )
    html = replace_once(
        html,
        r'<article class="card">.*?</article>',
        article,
        "daily reading",
    )

    today_words_js = json.dumps(day["words"], ensure_ascii=False)
    html = replace_once(
        html,
        r"function renderToday\(\)\{todays\.innerHTML=\[.*?\]\.map",
        f"function renderToday(){{todays.innerHTML={today_words_js}.map",
        "Today's 5",
    )

    comp = day["comprehension"]
    option_html = "".join(
        f'<button class="option" data-correct="{1 if i == comp["correct"] else 0}">{html_escape(opt)}</button>'
        for i, opt in enumerate(comp["options"])
    )
    comp_block = (
        '<div class="exercise"><div class="eyebrow">1 · Comprehension</div>'
        f'<p><b>{html_escape(comp["question"])}</b></p>{option_html}</div>'
    )
    html = replace_once(
        html,
        r'<div class="exercise"><div class="eyebrow">1 · Comprehension</div>.*?</div>'
        r'(?=<div class="exercise"><div class="eyebrow">2 · Rewrite</div>)',
        comp_block,
        "comprehension exercise",
    )

    ex = day["rewrite_examples"]
    examples = (
        f'<b>Clear:</b> {html_escape(ex["clear"])}<br><br>'
        f'<b>More articulate:</b> {html_escape(ex["articulate"])}<br><br>'
        f'<b>Analytical:</b> {html_escape(ex["analytical"])}'
    )
    rewrite_block = (
        '<div class="exercise"><div class="eyebrow">2 · Rewrite</div>'
        f'<p><b>Improve without making it unnecessarily complicated:</b> {html_escape(day["rewrite_prompt"])}</p>'
        '<textarea id="rewrite" placeholder="Write your version..."></textarea>'
        '<button class="primary" id="reveal" style="margin-top:10px">Reveal examples</button>'
        f'<div id="examples" class="callout hidden" style="margin-top:10px">{examples}</div></div>'
    )
    html = replace_once(
        html,
        r'<div class="exercise"><div class="eyebrow">2 · Rewrite</div>.*?</div>'
        r'(?=<div class="exercise"><div class="eyebrow">3 · Speak</div>)',
        rewrite_block,
        "rewrite exercise",
    )

    try_words = " · ".join(day["words"][:3])
    speaking_block = (
        '<div class="exercise"><div class="eyebrow">3 · Speak</div>'
        f'<p><b>60-second prompt:</b> {html_escape(day["speaking_prompt"])}</p>'
        f'<p class="small">Try using: {html_escape(try_words)}</p></div>'
    )
    html = replace_once(
        html,
        r'<div class="exercise"><div class="eyebrow">3 · Speak</div>.*?</div>(?=</section>)',
        speaking_block,
        "speaking exercise",
    )

    INDEX.write_text(html, encoding="utf-8")
    print(f"Applied Lexicon content for {day['date']}: {day['title']}")


if __name__ == "__main__":
    main()
