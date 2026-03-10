# RareNav — AI-Powered Rare Disease Navigator | AI 驱动的罕见病导航系统

**[English](#english) | [中文](#chinese)**

---

<a name="english"></a>

# RareNav — AI-Powered Rare Disease Navigator

> **MedGemma 4B · ClinVar 5M+ variants · HPO Ontology · Agentic Pipeline**
> Reducing the 5–7 year rare disease diagnostic odyssey with on-premises multimodal AI.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Model: MedGemma 4B](https://img.shields.io/badge/Model-MedGemma%204B-green)](https://huggingface.co/google/medgemma-4b-it)
[![Kaggle: MedGemma Impact Challenge](https://img.shields.io/badge/Kaggle-MedGemma%20Impact%20Challenge-orange)](https://www.kaggle.com/competitions/med-gemma-impact-challenge)

---

## 🚀 Try it Now

**Live Demo:** [https://muddy-resonance-cffd.542058929.workers.dev/](https://muddy-resonance-cffd.542058929.workers.dev/)

> If the page doesn't load on first visit, please refresh once. The demo runs on a single GPU and may take a moment to warm up.

---

## The Problem

Rare diseases affect **~300 million people** worldwide. The average patient endures a **5–7 year diagnostic odyssey**, receives **3+ misdiagnoses**, and faces enormous emotional and financial burden — often without ever getting a name for their condition.

The bottleneck is not a lack of medical knowledge. It's access: access to specialists, access to genomic databases, and access to AI that can reason over complex multi-modal clinical data.

RareNav is built to close that gap.

---

## What is RareNav?

RareNav is a full-stack clinical decision support platform combining:

- **MedGemma 4B IT** (Google HAI-DEF) — multimodal medical AI for text and vision reasoning
- **ClinVar** — 5M+ curated clinical variant submissions from NCBI
- **Human Phenotype Ontology (HPO)** — 13,000+ standardized clinical terms
- **Curated Rare Disease Knowledge Base** — 50+ diseases with genetics, symptoms, diagnostics, and treatments

The system runs **fully on-premises** — no patient data ever leaves the institution.

---

## Core Features

### 🧬 Multimodal Genetic Report Upload
Upload a genetic test PDF or image. MedGemma's vision model automatically extracts all variants, classifications, and lab metadata — no manual entry required.

### 🗄 Variant Database
Real-time search across 5M+ ClinVar variants. Each result includes AI-generated patient-facing explanations, ACMG classification badges, ClinVar links, and PubMed references.

### 🔍 Symptom Navigator
Enter free-text symptoms in plain language. RareNav maps them to HPO terms, then uses MedGemma to generate a rare disease differential diagnosis ranked by clinical relevance.

### 🤖 Agentic Diagnostic Pipeline
The core innovation: a multi-step agentic workflow that chains ClinVar lookup → HPO mapping → MedGemma reasoning → structured clinical report generation. Tool calls are visualized in real-time as the pipeline executes.

### 💬 Dual-Mode AI Chat (Streaming)
- **Patient mode** — plain language, empathetic explanations
- **Clinician mode** — ACMG criteria, clinical terminology, differential reasoning

Responses stream token-by-token over SSE. Follow-up question prompts are generated automatically based on conversation context.

### 📖 Disease Library
50+ rare disease profiles with inheritance patterns, prevalence, diagnostic criteria, treatment options, specialists, and direct links to OMIM, ClinVar, and ClinicalTrials.gov.

---

## Why This Fits the MedGemma Impact Challenge

RareNav demonstrates MedGemma across **five distinct clinical tasks** in a single integrated platform:

| Task | MedGemma Capability Used |
|------|--------------------------|
| Variant explanation | Text reasoning + medical knowledge |
| Symptom-to-diagnosis | Clinical NLP + rare disease reasoning |
| Report synthesis | Multi-call agentic orchestration |
| PDF/image extraction | Vision model (multimodal) |
| Conversational chat | Instruction following + streaming |

The agentic pipeline directly addresses the **Agentic Workflow Prize** track: MedGemma is orchestrated across multiple sequential tool calls with real-time intermediate outputs, context management across turns, and structured final report generation.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Flask Backend                       │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  MedGemma   │  │   ClinVar    │  │  HPO Service   │  │
│  │  4B IT      │  │  8.6M rows   │  │  18K terms     │  │
│  │  (fp32 GPU) │  │  (SQLite)    │  │  (in-memory)   │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  SSE Streaming  │  Agent Orchestration           │    │
│  │  /api/chat/stream  →  tool_start / token / done  │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP + SSE
┌──────────────────────▼──────────────────────────────────┐
│              Single-File HTML Frontend                   │
│    (Embedded in frontend.py — no npm build required)     │
│                                                          │
│   Chat UI  │  Variant DB  │  Disease Library  │  Upload  │
└─────────────────────────────────────────────────────────┘
```

**Stack:** Python · Flask · MedGemma 4B · SQLite · Vanilla JS · SSE streaming

**Key design principle:** `python app.py` is all you need. Zero frontend build steps.

---

## Local Deployment

### Requirements

- Python 3.10+
- CUDA GPU with ≥16GB VRAM (tested on NVIDIA RTX 2080 Ti / T4 / A100)
- 32GB+ system RAM recommended
- Conda environment recommended

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/IveGotMagicBean/RareNav_MedGemma.git
cd RareNav_MedGemma

# 2. Create and activate conda environment
conda create -n rarenav python=3.10
conda activate rarenav

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Download MedGemma 4B
# Model page: https://huggingface.co/google/medgemma-4b-it
# Requires a Hugging Face account and acceptance of the model license
huggingface-cli login
huggingface-cli download google/medgemma-4b-it --local-dir ./model_data/medgemma-4b-it

# 5. Launch
python app.py
```

Open your browser at `http://localhost:5000`.

### SLURM Cluster Deployment

```bash
sbatch app.sh
# Monitor: tail -f app.err
# Access:  http://<node-ip>:5000
```

---

## Performance

| Metric | Value |
|--------|-------|
| Model | MedGemma 4B IT (fp32) |
| ClinVar variants indexed | 8,678,497 |
| HPO terms loaded | 18,252 |
| Typical response latency | 15–45s |
| Concurrent users supported | 1 (single GPU, sequential) |

---

## Disclaimer

RareNav is a **research tool** and is **not a medical device**. All outputs should be reviewed by qualified healthcare professionals.

---

## License

MIT License. MedGemma is developed by Google and subject to its own [terms of use](https://huggingface.co/google/medgemma-4b-it). ClinVar data provided by NCBI (public domain). HPO maintained by the Monarch Initiative (CC BY 4.0).

---

<a name="chinese"></a>

# RareNav — AI 驱动的罕见病导航系统

> **MedGemma 4B · ClinVar 500万+ 变异 · HPO 本体 · 智能体诊断流水线**
> 以本地部署的多模态医学 AI，缩短罕见病患者 5~7 年的诊断马拉松。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![模型: MedGemma 4B](https://img.shields.io/badge/模型-MedGemma%204B-green)](https://huggingface.co/google/medgemma-4b-it)
[![比赛: MedGemma Impact Challenge](https://img.shields.io/badge/Kaggle-MedGemma%20Impact%20Challenge-orange)](https://www.kaggle.com/competitions/med-gemma-impact-challenge)

---

## 🚀 在线体验

**在线 Demo：** [https://muddy-resonance-cffd.542058929.workers.dev/](https://muddy-resonance-cffd.542058929.workers.dev/)

> 如果首次访问页面未加载，刷新一次即可。Demo 运行在单块 GPU 上，首次响应可能需要片刻。

---

## 背景与问题

罕见病影响全球约 **3 亿人**，但平均每位患者需要等待 **5~7 年** 才能获得正确诊断，途中平均经历 **3 次以上误诊**，承受巨大的身心与经济负担——很多人终其一生都无法得到一个病名。

瓶颈不在于医学知识的缺失，而在于**获取渠道的缺失**：缺少可及的专科医生、缺少对基因组数据库的访问能力、缺少能够推理复杂多模态临床数据的 AI 工具。

RareNav 正是为此而生。

---

## 项目简介

RareNav 是一套全栈临床决策支持平台，整合了：

- **MedGemma 4B IT**（Google HAI-DEF）——支持文本与视觉推理的多模态医学大模型
- **ClinVar**——NCBI 收录的 500 万+ 临床变异数据
- **人类表型本体（HPO）**——13,000+ 标准化临床术语
- **罕见病知识库**——50+ 种疾病的遗传背景、症状、诊断标准与治疗方案

系统**完全本地部署**，患者数据不离开机构网络。

---

## 核心功能

### 🧬 多模态基因报告上传
上传基因检测 PDF 或图片，MedGemma 视觉模型自动提取所有变异位点、分类结果及实验室数据，无需手动录入。

### 🗄 变异数据库
跨 500 万+ ClinVar 变异的实时检索。每条结果配有 AI 生成的患者友好解释、ACMG 分类标签、ClinVar 链接及 PubMed 参考文献。

### 🔍 症状导航
用自然语言描述症状，系统自动映射至 HPO 标准术语，再由 MedGemma 生成按临床相关性排序的罕见病鉴别诊断列表。

### 🤖 智能体诊断流水线
核心创新：多步骤智能体工作流，串联 ClinVar 查询 → HPO 映射 → MedGemma 推理 → 结构化临床报告生成。工具调用状态在界面实时可视化。

### 💬 双模式 AI 对话（流式输出）
- **患者模式**——通俗语言，关怀导向的解释
- **临床医生模式**——ACMG 标准，专业临床术语，鉴别推理

### 📖 疾病图书馆
50+ 种罕见病档案，包含遗传方式、患病率、诊断标准、治疗选项，并直连 OMIM、ClinVar 和 ClinicalTrials.gov。

---

## 参赛亮点

RareNav 在**单一集成平台**中展示了 MedGemma 的五类临床任务能力：

| 任务 | 使用的 MedGemma 能力 |
|------|----------------------|
| 变异解读 | 文本推理 + 医学知识 |
| 症状到诊断 | 临床 NLP + 罕见病推理 |
| 报告综合生成 | 多轮智能体编排 |
| PDF/图片信息提取 | 视觉模型（多模态） |
| 对话式咨询 | 指令跟随 + 流式输出 |

智能体流水线直接对应 **Agentic Workflow Prize** 赛道。

---

## 本地部署

```bash
# 1. 克隆仓库
git clone https://github.com/IveGotMagicBean/RareNav_MedGemma.git
cd RareNav_MedGemma

# 2. 创建环境
conda create -n rarenav python=3.10
conda activate rarenav
pip install -r backend/requirements.txt

# 3. 下载模型（模型页面：https://huggingface.co/google/medgemma-4b-it）
huggingface-cli login
huggingface-cli download google/medgemma-4b-it --local-dir ./model_data/medgemma-4b-it

# 4. 启动
python app.py
# 浏览器访问 http://localhost:5000
```

---

## 免责声明

RareNav 是**研究工具**，**不是医疗器械**，所有输出结果应由具有资质的医疗专业人员审核。

---

## 许可证

MIT 许可证。MedGemma 由 Google 开发，受其[使用条款](https://huggingface.co/google/medgemma-4b-it)约束。ClinVar 数据由 NCBI 提供（公共领域）。HPO 由 Monarch Initiative 维护（CC BY 4.0）。
