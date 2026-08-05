# 旅游评论大模型数据标注与评测

> 一个面向AI数据标注与大模型评测岗位的个人实践项目，围绕旅游评论完成标签体系设计、Prompt迭代、自动化评测与Bad Case分析。

## 在线演示入口

**在线演示：** [https://ai.4399yskp.online](https://ai.4399yskp.online)
GitHub 仓库：[tourism-review-llm-evaluation](https://github.com/yshk9364-ux/tourism-review-llm-evaluation)

## GitHub项目特点

- 覆盖情感分类、问题类型识别、证据提取和复核判断。
- 提供数据检查、Prompt 对比、指标计算和 Bad Case 导出的完整链路。
- 使用 Python + pandas 实现，支持本地运行和 Nginx 静态部署。

## 项目背景

旅游评论同时包含服务、排队、价格、环境等多类反馈。项目将非结构化评论转为统一标签，并比较两版 Prompt 在复杂表达和多标签任务中的表现，为数据质检和模型分析提供可复现的参考流程。

## 项目流程

```text
数据构建 → 标签规范 → Prompt设计 → 模型输出 → 自动评测 → Bad Case分析
```

## 标签体系

| 字段 | 说明 |
| --- | --- |
| sentiment | 正面、 中性、负面 |
| issue_category | 服务、排队、价格、卫生、餐饮、交通、设施、景色、宣传、其他、无明显问题；支持多标签，以 `;` 分隔 |
| evidence | 与判断对应的评论原文片段 |
| need_review | 需要进一步关注的复杂表达标记 |

`data/gold_dataset.csv` 作为项目的**基准标签集**，用于对比两版 Prompt 的结构化输出。

## Prompt V1与V2对比

| 维度 | Prompt V1 | Prompt V2 |
| --- | --- | --- |
| 任务描述 | 基础任务要求 | 明确标签定义与判断范围 |
| 多标签 | 仅输出字段 | 要求保留全部独立主题 |
| 证据 | 提取证据 | 约束证据来自评论原文 |
| 边界场景 | 规则较少 | 覆盖反讽、模糊和混合情感 |
| 输出 | 字段清单 | 固定格式与 Few-shot 示例 |

## 评测结果

以下结果由 `scripts/evaluate.py` 根据当前基准标签集计算。

| 指标 | V1 | V2 |
| --- | ---: | ---: |
| 情感分类准确率 | 67.5% | 100.0% |
| 问题类型完全匹配率 | 40.0% | 95.0% |
| 问题类型标签级 Precision | 97.5% | 100.0% |
| 问题类型标签级 Recall | 60.9% | 96.9% |
| 问题类型标签级 F1 | 75.0% | 98.4% |
| 证据可定位率 | 100.0% | 100.0% |
| 输出完整率 | 100.0% | 100.0% |
| need_review 准确率 | 72.5% | 100.0% |

## Bad Case分析

| 评论场景 | V1 现象 | V2 优化 |
| --- | --- | --- |
| 反讽表达 | 容易按字面褒义判断 | 按实际体验识别反讽并标记复核 |
| 正负混合 | 容易只保留单一方向信息 | 保留多个主题，整体判断更稳定 |
| 多问题评论 | 容易漏掉第二个问题类型 | 使用多标签规则覆盖独立主题 |
| 信息不足 | 容易给出过度确定的结论 | 使用复核标记保留判断边界 |

完整样本与错误类型见 [evaluation/bad_cases.csv](evaluation/bad_cases.csv)。

## 技术栈

- Python 3.9+
- pandas
- CSV / UTF-8 数据处理
- Prompt Engineering
- 原生 HTML、CSS、JavaScript
- Nginx 静态网站部署

## 项目结构

```text
tourism-review-llm-evaluation/
├── data/          # 评论数据、基准标签集、两版模型输出
├── guidelines/    # 标签规范与质检清单
├── prompts/       # Prompt V1 与 V2
├── scripts/       # 数据检查与自动评测脚本
├── evaluation/    # 指标、Bad Case 与评测报告
├── docs/          # 项目说明与求职材料
├── site/          # 可部署的项目展示网站
└── deploy/        # Nginx 配置与部署脚本
```

## 本地运行方式

建议 Python 3.9+，所有 CSV 使用 UTF-8 编码。

```bash
python3 -m pip install -r requirements.txt
python3 scripts/validate_data.py
python3 scripts/evaluate.py
```

本地预览网站：

```bash
cd site
python3 -m http.server 8000
```

浏览器访问 `http://localhost:8000`。

## 项目成果

- 建立了适用于旅游评论的多标签标注规范与质检检查清单。
- 完成了两版 Prompt 的结构化输出对比与 8 项自动评测指标计算。
- 自动导出 Bad Case，支持对反讽、混合情感和多问题样本进行针对性分析。
- 提供原生静态展示网站及 Ubuntu / Debian Nginx 部署脚本。

## 作者职责

- 设计测试评论、标签字段和标注规则。
- 编写 Prompt V1、Prompt V2 及其结构化输出要求。
- 使用 pandas 编写数据检查、指标计算和 Bad Case 导出脚本。
- 编写评测报告、项目展示页面和静态部署配置。

## 数据说明

项目使用40条自建旅游评论测试数据，用于验证数据标注、Prompt优化和模型评测的完整流程。
