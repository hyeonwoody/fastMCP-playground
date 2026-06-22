from __future__ import annotations

import re


async def clean(raw_text: str, content_type: str) -> str:
    text = raw_text
    if content_type == "html":
        text = _strip_html_boilerplate(text)
    text = _normalize_whitespace(text)
    text = _fix_encoding(text)
    return text.strip()


def _strip_html_boilerplate(text: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<nav[^>]*>.*?</nav>", "", text, flags=re.DOTALL)
    text = re.sub(r"<footer[^>]*>.*?</footer>", "", text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    return text


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\t", "    ", text)
    text = re.sub(r" {4,}", "    ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _fix_encoding(text: str) -> str:
    replacements = {
        " ": " ",
        "​": "",
        "﻿": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text