#!/usr/bin/env python3
"""Deterministic lint for Douni platform titles.

This script reports structural and compliance warnings. It does not attempt to
judge whether a title is creative or faithful to the source script.
"""

from __future__ import annotations

import argparse
import json
import re
import sys


HARD_BANS = (
    "全网第一",
    "百分百",
    "100%",
    "保证爆",
    "必火",
)

TEMPLATE_WARNINGS = (
    "绝绝子",
    "闭眼冲",
    "封神",
    "天花板",
    "保姆级",
    "一招教会你",
    "神仙工作",
)

INTERNAL_TERMS = (
    "客户反馈",
    "实际合作价",
    "报价",
    "供应商",
    "机构归属",
    "内审不通过",
    "客户不通过",
)


def visible_length(value: str) -> int:
    clean = re.sub(r"#[^\s#]+", "", value)
    clean = re.sub(r"\s+", "", clean)
    return len(clean)


def lint(platform: str, title: str) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    length = visible_length(title)

    if not title.strip():
        errors.append("标题为空")
    if any(term.casefold() in title.casefold() for term in HARD_BANS):
        errors.append("包含不可验证的绝对承诺")
    if any(term in title for term in INTERNAL_TERMS):
        errors.append("包含内部业务信息")
    matched_templates = [term for term in TEMPLATE_WARNINGS if term in title]
    if matched_templates:
        warnings.append("包含低稳定性模板词：" + "、".join(matched_templates))
    if title.count("!") + title.count("！") + title.count("?") + title.count("？") > 2:
        warnings.append("标点过多")
    if len(re.findall(r"#[^\s#]+", title)) > 0:
        warnings.append("话题标签应与标题正文分开")
    emoji_count = len(re.findall(r"[\U0001F300-\U0001FAFF]", title))
    if emoji_count > 1:
        warnings.append("emoji 超过 1 个")

    if platform == "xiaohongshu" and not 12 <= length <= 22:
        warnings.append(f"小红书标题通常为 12–22 字，当前为 {length} 字")
    if platform == "douyin" and not 10 <= length <= 30:
        warnings.append(f"抖音标题通常为 10–30 字，当前为 {length} 字")

    return {
        "ok": not errors,
        "platform": platform,
        "title": title,
        "visibleLength": length,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=("douyin", "xiaohongshu"), required=True)
    parser.add_argument("--title", action="append", required=True)
    args = parser.parse_args()
    results = [lint(args.platform, title) for title in args.title]
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    return 0 if all(item["ok"] for item in results) else 1


if __name__ == "__main__":
    sys.exit(main())
