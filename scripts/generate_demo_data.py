"""将项目自建旅游评论测试数据稳定扩展为 1000 条。

脚本保留数据文件中已有的前 40 条案例，并用固定模板生成其余 960 条。
这样再次运行时仍会得到相同的 review_id、标签和两版模拟输出，便于学习
数据构建、数据校验和 Prompt 评测的完整流程。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
BASE_COUNT = 40
TARGET_COUNT = 1000


def build_case(slot: int, cycle: int) -> dict[str, str]:
    """根据模板编号生成一条带有草稿基准标签的自建测试评论。"""
    entrances = ["东门", "南门", "游客中心", "索道口", "湖边入口"]
    days = ["周一上午", "周三下午", "周五傍晚", "周六上午", "节假日早上"]
    spots = ["云台观景台", "山谷栈道", "湖心步道", "古城墙", "森林小径"]
    foods = ["菌菇面", "竹筒饭", "热汤面", "本地小吃", "简餐"]
    entrance = entrances[cycle % len(entrances)]
    day = days[cycle % len(days)]
    spot = spots[cycle % len(spots)]
    food = foods[cycle % len(foods)]
    wait_minutes = 15 + (cycle % 6) * 10
    long_wait = 50 + (cycle % 5) * 20
    price = 45 + (cycle % 4) * 15

    cases = [
        (f"{entrance}的工作人员主动帮我们指路，还提醒了安全事项。", "正面", "服务", "否"),
        (f"咨询{spot}怎么走时，工作人员一直低头玩手机，没有回应。", "负面", "服务", "否"),
        (f"{day}入园只等了{wait_minutes}分钟，检票安排比较顺畅。", "正面", "排队", "否"),
        (f"{day}在{entrance}排了{long_wait}分钟，现场也没人说明原因。", "负面", "排队;服务", "否"),
        (f"门票{price}元，包含接驳车和展馆，整体可以接受。", "正面", "价格", "否"),
        (f"门票{price}元还要另收摆渡车费，感觉价格不太合理。", "负面", "价格;交通", "否"),
        (f"{spot}附近没有垃圾，洗手间也很整洁。", "正面", "卫生", "否"),
        (f"洗手间有异味，垃圾桶旁边还有没清理的纸巾。", "负面", "卫生", "否"),
        (f"景区里的{food}热乎，分量也刚好，休息时吃得很舒服。", "正面", "餐饮", "否"),
        (f"{food}又冷又咸，价格还比门口餐馆高不少。", "负面", "餐饮;价格", "否"),
        (f"从地铁站出来有直达接驳车，到{entrance}很省心。", "正面", "交通", "否"),
        (f"返程接驳车间隔太久，最后只能步行很远去找公交。", "负面", "交通", "否"),
        (f"{spot}的栈道和座椅维护得不错，老人走起来也方便。", "正面", "设施", "否"),
        (f"观景台护栏松动，几个指示牌也褪色看不清。", "负面", "设施", "否"),
        (f"傍晚在{spot}看日落很开阔，照片比预想更有层次。", "正面", "景色", "否"),
        (f"当天大雾，{spot}几乎看不见远处，体验只能说一般。", "中性", "景色", "是"),
        (f"宣传图里的花海面积很大，实际只有入口一小片，落差明显。", "负面", "宣传", "否"),
        ("慢慢逛了半天，没有特别惊喜，也没有明显不舒服的地方。", "中性", "无明显问题", "否"),
        (f"{spot}景色很好，但路边垃圾较多，工作人员清扫不及时。", "中性", "景色;卫生;服务", "是"),
        (f"门票不贵，不过{entrance}排队太久，进园后心情已经受影响。", "中性", "价格;排队", "是"),
        (f"真有效率，在{entrance}晒了半小时，工作人员一直让我们再等等。", "负面", "排队;服务", "是"),
        ("朋友说这里适合亲子游，我没有实际去过，暂时无法评价。", "中性", "其他", "是"),
        (f"{food}味道普通，套餐却比菜单标价多收了十元。", "负面", "餐饮;价格", "否"),
        (f"停车场到{spot}有无障碍坡道和休息座椅，带长辈出行比较方便。", "正面", "交通;设施", "否"),
    ]
    review_text, sentiment, issue_category, need_review = cases[slot]
    return {
        "review_text": review_text,
        "sentiment": sentiment,
        "issue_category": issue_category,
        "evidence": review_text.rstrip("。"),
        "need_review": need_review,
    }


def split_labels(value: str) -> list[str]:
    """按项目约定拆分英文分号连接的标签。"""
    return [item for item in value.split(";") if item]


def make_v1_output(case: dict[str, str], record_number: int, slot: int) -> dict[str, str]:
    """模拟基础 Prompt：复杂表达更易漏标、误判或缺少复核。"""
    predicted = {
        "sentiment": case["sentiment"],
        "issue_category": case["issue_category"],
        "evidence": case["evidence"],
        "need_review": case["need_review"],
    }

    # 多主题、反讽和信息不足是基础提示词的主要薄弱点。
    if slot == 3:
        predicted["issue_category"] = "排队"
    elif slot == 5:
        predicted["issue_category"] = "价格"
    elif slot == 9:
        predicted["issue_category"] = "餐饮"
    elif slot == 18:
        predicted["sentiment"] = "正面"
        predicted["issue_category"] = "景色"
        predicted["need_review"] = "否"
    elif slot == 19:
        predicted["sentiment"] = "负面"
        predicted["issue_category"] = "排队"
        predicted["need_review"] = "否"
    elif slot == 20:
        predicted["sentiment"] = "正面"
        predicted["issue_category"] = "服务"
        predicted["need_review"] = "否"
    elif slot == 21:
        predicted["issue_category"] = "无明显问题"
        predicted["need_review"] = "否"
    elif slot == 22:
        predicted["issue_category"] = "餐饮"
    elif slot == 23:
        predicted["issue_category"] = "交通"
    elif record_number % 17 == 0:
        # 只保留多标签中的第一个主题，模拟问题漏标。
        predicted["issue_category"] = split_labels(case["issue_category"])[0]

    if record_number % 13 == 0:
        # 不在原文中的概括性表达会被评测为证据错误。
        predicted["evidence"] = "整体体验不错"
    elif record_number % 7 == 0:
        # 证据缩短但仍可在原文找到。
        predicted["evidence"] = case["review_text"].split("，")[0]
    return predicted


def make_v2_output(case: dict[str, str], record_number: int) -> dict[str, str]:
    """模拟规则增强 Prompt：绝大多数遵循标签、证据和复核规则。"""
    predicted = {
        "sentiment": case["sentiment"],
        "issue_category": case["issue_category"],
        "evidence": case["evidence"],
        "need_review": case["need_review"],
    }
    # 保留少量可分析的错误，避免将演示结果包装成完全无误。
    if record_number % 211 == 0 and ";" in case["issue_category"]:
        predicted["issue_category"] = split_labels(case["issue_category"])[0]
    if record_number % 233 == 0:
        predicted["evidence"] = "体验很好"
    if record_number % 271 == 0:
        predicted["need_review"] = "否" if case["need_review"] == "是" else "是"
    if record_number % 307 == 0:
        predicted["sentiment"] = "中性" if case["sentiment"] != "中性" else "负面"
    return predicted


def read_base_data(filename: str, columns: list[str]) -> pd.DataFrame:
    """读取前 40 条已有案例；脚本重跑时只使用这部分作为固定种子。"""
    path = DATA_DIR / filename
    df = pd.read_csv(path, encoding="utf-8", dtype=str)
    if len(df) < BASE_COUNT:
        raise ValueError(f"{filename} 少于 {BASE_COUNT} 条，无法保留原始案例。")
    missing = set(columns) - set(df.columns)
    if missing:
        raise ValueError(f"{filename} 缺少字段：{sorted(missing)}")
    return df.loc[: BASE_COUNT - 1, columns].copy()


def main() -> None:
    raw_columns = ["review_id", "review_text"]
    gold_columns = [
        "review_id", "review_text", "sentiment", "issue_category", "evidence",
        "need_review", "reviewed_by_human",
    ]
    output_columns = ["review_id", "sentiment", "issue_category", "evidence", "need_review"]
    raw = read_base_data("raw_reviews.csv", raw_columns)
    gold = read_base_data("gold_dataset.csv", gold_columns)
    output_v1 = read_base_data("model_outputs_v1.csv", output_columns)
    output_v2 = read_base_data("model_outputs_v2.csv", output_columns)

    generated_raw: list[dict[str, str]] = []
    generated_gold: list[dict[str, str]] = []
    generated_v1: list[dict[str, str]] = []
    generated_v2: list[dict[str, str]] = []
    for record_number in range(BASE_COUNT + 1, TARGET_COUNT + 1):
        position = record_number - BASE_COUNT - 1
        slot = position % 24
        cycle = position // 24
        case = build_case(slot, cycle)
        review_id = f"R{record_number:04d}"
        generated_raw.append({"review_id": review_id, "review_text": case["review_text"]})
        generated_gold.append({
            "review_id": review_id,
            "review_text": case["review_text"],
            "sentiment": case["sentiment"],
            "issue_category": case["issue_category"],
            "evidence": case["evidence"],
            "need_review": case["need_review"],
            "reviewed_by_human": "否",
        })
        generated_v1.append({"review_id": review_id, **make_v1_output(case, record_number, slot)})
        generated_v2.append({"review_id": review_id, **make_v2_output(case, record_number)})

    pd.concat([raw, pd.DataFrame(generated_raw)], ignore_index=True).to_csv(
        DATA_DIR / "raw_reviews.csv", index=False, encoding="utf-8"
    )
    pd.concat([gold, pd.DataFrame(generated_gold)], ignore_index=True).to_csv(
        DATA_DIR / "gold_dataset.csv", index=False, encoding="utf-8"
    )
    pd.concat([output_v1, pd.DataFrame(generated_v1)], ignore_index=True).to_csv(
        DATA_DIR / "model_outputs_v1.csv", index=False, encoding="utf-8"
    )
    pd.concat([output_v2, pd.DataFrame(generated_v2)], ignore_index=True).to_csv(
        DATA_DIR / "model_outputs_v2.csv", index=False, encoding="utf-8"
    )
    print(f"已生成 {TARGET_COUNT} 条自建旅游评论测试数据。")
    print("前 40 条为原有案例；其余 960 条由固定模板生成，全部保留 reviewed_by_human=否。")


if __name__ == "__main__":
    main()
