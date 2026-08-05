"""比较两个 Prompt 版本的模拟模型输出，并导出指标和 Bad Case。"""

from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
EVAL_DIR = ROOT / "evaluation"
REQUIRED_OUTPUT_COLUMNS = ["review_id", "sentiment", "issue_category", "evidence", "need_review"]


def split_labels(value: str) -> set[str]:
    """将英文分号分隔的多标签转换为集合。"""
    return {item.strip() for item in str(value).split(";") if item.strip()}


def classify_error(row: pd.Series) -> tuple[str, str]:
    """根据逐字段差异生成简明、可解释的错误分类。"""
    issues: list[str] = []
    if row["gold_sentiment"] != row["predicted_sentiment"]:
        issues.append("情感误判")
    gold_labels = split_labels(row["gold_issue_category"])
    predicted_labels = split_labels(row["predicted_issue_category"])
    if not gold_labels.issubset(predicted_labels):
        issues.append("问题漏标")
    if not predicted_labels.issubset(gold_labels):
        issues.append("问题多标")
    if not bool(row["evidence_found"]):
        issues.append("证据错误")
    if row["gold_need_review"] != row["predicted_need_review"]:
        issues.append("复核判断错误")

    if len(issues) > 1:
        error_type = "多项错误"
    else:
        error_type = issues[0]
    analysis = "；".join(issues)
    return error_type, analysis


def evaluate_version(gold: pd.DataFrame, predicted: pd.DataFrame, version: str) -> tuple[dict[str, object], pd.DataFrame]:
    """计算单个版本的指标，并返回逐条对齐结果。"""
    missing = set(REQUIRED_OUTPUT_COLUMNS) - set(predicted.columns)
    if missing:
        raise ValueError(f"{version} 缺少字段：{sorted(missing)}")
    merged = gold.merge(predicted, on="review_id", suffixes=("_gold", "_pred"), how="left", validate="one_to_one")
    merged = merged.rename(columns={
        "review_text_gold": "review_text",
        "sentiment_gold": "gold_sentiment", "sentiment_pred": "predicted_sentiment",
        "issue_category_gold": "gold_issue_category", "issue_category_pred": "predicted_issue_category",
        "evidence_gold": "gold_evidence", "evidence_pred": "predicted_evidence",
        "need_review_gold": "gold_need_review", "need_review_pred": "predicted_need_review",
    })
    merged["evidence_found"] = merged.apply(
        lambda row: isinstance(row["predicted_evidence"], str) and row["predicted_evidence"] in row["review_text"], axis=1
    )
    # 合并后预测字段会带 _pred 后缀；用它们检查每条输出是否完整。
    merged["output_complete"] = merged[[
        "predicted_sentiment", "predicted_issue_category", "predicted_evidence", "predicted_need_review"
    ]].notna().all(axis=1)

    tp = fp = fn = 0
    for _, row in merged.iterrows():
        gold_labels = split_labels(row["gold_issue_category"])
        pred_labels = split_labels(row["predicted_issue_category"])
        tp += len(gold_labels & pred_labels)
        fp += len(pred_labels - gold_labels)
        fn += len(gold_labels - pred_labels)
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0

    metrics = {
        "prompt_version": version,
        "sample_size": len(merged),
        "sentiment_accuracy": (merged["gold_sentiment"] == merged["predicted_sentiment"]).mean(),
        "issue_exact_match_rate": (merged["gold_issue_category"] == merged["predicted_issue_category"]).mean(),
        "issue_label_precision": precision,
        "issue_label_recall": recall,
        "issue_label_f1": f1,
        "evidence_found_rate": merged["evidence_found"].mean(),
        "output_completeness_rate": merged["output_complete"].mean(),
        "need_review_accuracy": (merged["gold_need_review"] == merged["predicted_need_review"]).mean(),
    }
    return metrics, merged


def main() -> int:
    EVAL_DIR.mkdir(exist_ok=True)
    gold = pd.read_csv(DATA_DIR / "gold_dataset.csv", encoding="utf-8")
    results: list[dict[str, object]] = []
    bad_cases: list[pd.DataFrame] = []

    for version in ("v1", "v2"):
        predicted = pd.read_csv(DATA_DIR / f"model_outputs_{version}.csv", encoding="utf-8")
        metrics, merged = evaluate_version(gold, predicted, version.upper())
        results.append(metrics)
        incorrect = merged[
            (merged["gold_sentiment"] != merged["predicted_sentiment"])
            | (merged["gold_issue_category"] != merged["predicted_issue_category"])
            | (~merged["evidence_found"])
            | (merged["gold_need_review"] != merged["predicted_need_review"])
        ].copy()
        if not incorrect.empty:
            error_info = incorrect.apply(classify_error, axis=1, result_type="expand")
            incorrect[["error_type", "analysis"]] = error_info
            incorrect["prompt_version"] = version.upper()
            bad_cases.append(incorrect[[
                "review_id", "review_text", "prompt_version", "gold_sentiment", "predicted_sentiment",
                "gold_issue_category", "predicted_issue_category", "gold_evidence", "predicted_evidence",
                "error_type", "analysis",
            ]])

    metrics_df = pd.DataFrame(results)
    metrics_df.to_csv(EVAL_DIR / "metrics.csv", index=False, encoding="utf-8")
    pd.concat(bad_cases, ignore_index=True).to_csv(EVAL_DIR / "bad_cases.csv", index=False, encoding="utf-8")
    print(metrics_df.to_string(index=False, float_format=lambda value: f"{value:.3f}"))
    print(f"已导出：{EVAL_DIR / 'metrics.csv'}")
    print(f"已导出：{EVAL_DIR / 'bad_cases.csv'}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"评测失败：{exc}")
        sys.exit(1)
