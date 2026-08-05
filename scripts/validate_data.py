"""检查模拟旅游评论数据及模型输出的基础质量。"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SENTIMENTS = {"正面", "中性", "负面"}
REVIEW_FLAGS = {"是", "否"}
GOLD_COLUMNS = [
    "review_id", "review_text", "sentiment", "issue_category", "evidence",
    "need_review", "reviewed_by_human",
]
OUTPUT_COLUMNS = ["review_id", "sentiment", "issue_category", "evidence", "need_review"]


def check_file(path: Path, required_columns: list[str]) -> tuple[pd.DataFrame | None, list[str]]:
    """读取一个 CSV，并返回发现的问题；所有 CSV 按 UTF-8 编码读取。"""
    errors: list[str] = []
    if not path.exists():
        return None, [f"文件不存在：{path.relative_to(ROOT)}"]
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except Exception as exc:  # 便于初学者查看读取失败原因
        return None, [f"无法读取 {path.name}：{exc}"]

    missing = set(required_columns) - set(df.columns)
    if missing:
        errors.append(f"{path.name} 缺少字段：{sorted(missing)}")
        return df, errors
    if df[required_columns].isna().any().any():
        errors.append(f"{path.name} 存在必填字段空值")
    if df["review_id"].duplicated().any():
        errors.append(f"{path.name} 存在重复 review_id")
    return df, errors


def main() -> int:
    errors: list[str] = []
    raw, raw_errors = check_file(DATA_DIR / "raw_reviews.csv", ["review_id", "review_text"])
    gold, gold_errors = check_file(DATA_DIR / "gold_dataset.csv", GOLD_COLUMNS)
    errors.extend(raw_errors + gold_errors)

    outputs: dict[str, pd.DataFrame] = {}
    for version in ("v1", "v2"):
        output, output_errors = check_file(DATA_DIR / f"model_outputs_{version}.csv", OUTPUT_COLUMNS)
        errors.extend(output_errors)
        if output is not None:
            outputs[version] = output
            # 模型输出也必须使用允许的情感、复核值。
            if not set(output["sentiment"].dropna()).issubset(SENTIMENTS):
                errors.append(f"model_outputs_{version}.csv 存在不合规情感标签")
            if not set(output["need_review"].dropna()).issubset(REVIEW_FLAGS):
                errors.append(f"model_outputs_{version}.csv 存在不合规 need_review 值")

    if gold is not None:
        if not set(gold["sentiment"].dropna()).issubset(SENTIMENTS):
            errors.append("gold_dataset.csv 存在不合规情感标签")
        if not set(gold["need_review"].dropna()).issubset(REVIEW_FLAGS):
            errors.append("gold_dataset.csv 存在不合规 need_review 值")
        if not set(gold["reviewed_by_human"].dropna()).issubset(REVIEW_FLAGS):
            errors.append("gold_dataset.csv 存在不合规 reviewed_by_human 值")

    if raw is not None:
        raw_ids = set(raw["review_id"])
        if gold is not None and set(gold["review_id"]) != raw_ids:
            errors.append("gold_dataset.csv 未与 raw_reviews.csv 完全一一对应")
        for version, output in outputs.items():
            if set(output["review_id"]) != raw_ids:
                errors.append(f"model_outputs_{version}.csv 未覆盖全部评论或存在额外评论")

    if errors:
        print("数据检查未通过：")
        for error in errors:
            print(f"- {error}")
        return 1
    sample_size = len(raw) if raw is not None else 0
    print(f"数据检查通过：4 个 CSV 文件字段完整，ID 无重复，标签合规，模型输出覆盖 {sample_size} 条评论。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
