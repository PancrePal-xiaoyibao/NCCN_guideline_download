# NCCN指南下载工具 v2.3 使用说明

## 概述

NCCN指南下载工具v2.3是一个优化的菜单式下载工具，支持6大主题分类、65种癌种筛选（含中英文别名）、语言筛选、PDF清单选择、MinerU/DeepSeek-OCR Markdown解析与RAG预处理。相比早期版本，v2.3提供了更完整的癌种覆盖、更灵活的下载选择和更安全的配置管理。

## 主要特性

### 🎯 核心功能
- **经典菜单 + 二级菜单**：选择主题后进入语言/癌种筛选
- **65种癌种**：完整覆盖 NCCN 官网癌种列表，含中英文别名自动映射
- **PDF清单选择**：解析后展示编号列表，支持 `1,3,5-8` 格式选择
- **语言筛选**：中文/英文/日语其他/全部，默认英文
- **CLI命令行**：`ncd` 命令支持 `interactive`、`download`、`list-cancers`、`convert`、`translate`
- **双重认证**：用户名密码 + Cookie认证
- **增量下载**：避免重复下载已有文件
- **完善日志**：详细操作记录和统计报告

### 🔒 安全性
- **本地配置**：使用 `config.json` 或 `.env`，不通过 Agent 交互收集密钥
- **请求频率控制**：2-5秒随机延迟
- **错误重试机制**：最多3次重试
- **URL域名白名单**：仅允许 `nccn.org` 域名下载
- **文件完整性验证**：PDF文件头和大小检查

### 📊 统计和监控
- **实时进度显示**：下载进度条（tqdm）
- **详细统计报告**：成功率、速度、耗时等
- **失败文件清单**：失败文件列表和重试选项
- **日志文件**：完整的操作记录

## 安装依赖

```bash
pip install requests beautifulsoup4 tqdm
```

如果`tqdm`未安装，工具会自动降级到简单进度显示。

## 使用方法

### 1. 交互式菜单

```bash
python download_NCCN_Guide_v2_menu.py
# 或
./ncd interactive
```

**主菜单**（选择主题）：

```
请选择要下载的主题:
============================================================
1. 癌症治疗指南英文版 (Treatment by Cancer Type - English Only)
   按癌症类型分类的治疗指南（英文版）
   目录: 01_Cancer_Treatment

2. 支持性护理指南 (Supportive Care)
   目录: 02_Supportive_Care

3. 患者指南英文版 (Patient Guidelines - English Only)
   目录: 03_Patient_Guidelines_English

4. 临床指南中文翻译 (Clinical Translations)
   目录: 04_Clinical_Translations

5. 患者指南中文翻译 (Patient Guidelines Translations)
   目录: 05_Patient_Translations

6. 患者指南中文版本 (Chinese Patient Guidelines)
   目录: 06_Chinese_Patient_Guidelines

7. 查看下载统计
8. 退出
```

**二级菜单**（选择主题后）：

```
============================================================
主题: 患者指南中文翻译 (Patient Guidelines Translations)
============================================================

📋 语言筛选:
0. 中文
1. 英文（默认）
2. 日语/其他语言
3. 全部
请选择语言 (0-3, 默认1): 0
✅ 语言筛选: 中文

🔍 正在获取PDF链接...
   主题: 患者指南中文翻译 (Patient Guidelines Translations)
   语言: 中文
   癌种: 全部

📋 解析到的 PDF 清单:
============================================================
  1. [Chinese] Guidelines for Patients® Bladder Cancer
     https://www.nccn.org/patients/guidelines/content/PDF/Bladder-zh-patient.pdf...
  2. [Chinese] Guidelines for Patients® Pancreatic Cancer
     https://www.nccn.org/patients/guidelines/content/PDF/pancreatic-patient-chinese-...
  ...
  15. [Chinese] Guidelines for Patients® Uterine Cancer
     https://www.nccn.org/patients/guidelines/content/PDF/uterine-ch-patient.pdf...
============================================================
  A. 全部下载 (15 个文件)
  输入编号选择，逗号分隔多个，如: 1,3,5-8
  直接回车 = 全部下载

请选择 (A/编号/回车=全部): 2
已选择 1 个文件进行下载。

=== 下载确认 ===
主题: 患者指南中文翻译 (Patient Guidelines Translations)
语言: 中文
癌种: 全部
确认后输入 Y 开始下载，其他键取消: Y
```

### 2. CLI 命令行

```bash
# 下载指定主题的指南
./ncd download --theme 1 --cancer breast --language 1 --yes

# 列出癌种
./ncd list-cancers --refresh

# PDF 转 Markdown
./ncd convert --input guide.pdf --output nccn_downloads/markdown/

# 使用 DeepSeek-OCR
./ncd convert --input guide.pdf --ocr-backend deepseek-ocr \
  --api-key sf-key --model deepseek-ai/DeepSeek-OCR

# 翻译 Markdown
./ncd translate --input guide.md --output guide.zh.md
```

### 3. 癌种筛选

支持 65 种癌种，中英文关键词自动映射：

| 输入 | 自动扩展为 |
|------|-----------|
| `胰腺` | `pancreatic adenocarcinoma, pancreatic, pancreas, 胰腺腺癌, 胰腺癌, 胰腺` |
| `乳腺` | `breast cancer, breast, 乳腺癌, 乳腺` |
| `肺` | `non-small cell lung cancer, nsclc, lung, 非小细胞肺癌, 肺癌, 肺` + `small cell lung cancer, sclc, lung, 小细胞肺癌, 肺癌, 肺` |

完整癌种列表（65种）：

Acute Lymphoblastic Leukemia, Acute Myeloid Leukemia, Ampullary Adenocarcinoma, Anal Carcinoma, Appendiceal Neoplasms, Basal Cell Skin Cancer, B-Cell Lymphomas, Biliary Tract Cancers, Bladder Cancer, Bone Cancer, Breast Cancer, Castleman Disease, Central Nervous System Cancers, Cervical Cancer, CLL/SLL, CML, Colon Cancer, Cutaneous Lymphomas, DFSP, Esophageal Cancers, Gastric Cancer, GIST, GTN, Hairy Cell Leukemia, Head and Neck Cancers, Hepatobiliary Cancers, Hepatocellular Carcinoma, Histiocytic Neoplasms, Hodgkin Lymphoma, Kaposi Sarcoma, Kidney Cancer, Melanoma (Cutaneous), Melanoma (Uveal), Merkel Cell Carcinoma, Mesothelioma (Peritoneal), Mesothelioma (Pleural), Multiple Myeloma, MDS, Myeloid/Lymphoid Neoplasms, MPN, Neuroblastoma, Neuroendocrine/Adrenal Tumors, NSCLC, Occult Primary, Ovarian Cancer, Pancreatic Adenocarcinoma, Pediatric ALL, Pediatric B-Cell Lymphoma, Pediatric CNS, Pediatric Hodgkin, Pediatric Soft Tissue Sarcoma, Penile Cancer, Prostate Cancer, Rectal Cancer, Small Bowel Adenocarcinoma, SCLC, Soft Tissue Sarcoma, Squamous Cell Skin Cancer, Systemic Light Chain Amyloidosis, Systemic Mastocytosis, T-Cell Lymphomas, Testicular Cancer, Thymomas/Thymic Carcinomas, Thyroid Carcinoma, Uterine Neoplasms, Vaginal Cancer, Vulvar Cancer, Waldenström Macroglobulinemia, Wilms Tumor

### 4. PDF 转 Markdown 与 RAG 预处理

**MinerU（默认）**：

```bash
./ncd convert --input guide.pdf --output nccn_downloads/markdown/
```

**DeepSeek-OCR（SiliconFlow 免费模型）**：

```bash
export SILICONFLOW_API_KEY="..."

./ncd convert --input guide.pdf --ocr-backend deepseek-ocr \
  --base-url https://api.siliconflow.cn/v1 \
  --model deepseek-ai/DeepSeek-OCR \
  --max-pages 0
```

生成文件：
- Markdown：`nccn_downloads/markdown/*.md`
- RAG chunks：`nccn_downloads/rag/*.chunks.jsonl`

**翻译为中文**（默认 SiliconFlow `glm-4.5-air`）：

```bash
export SILICONFLOW_API_KEY="..."

./ncd translate --input guide.md --output guide.zh.md
```

## 目录结构

```
nccn_downloads/
├── 01_Cancer_Treatment/          # 癌症治疗指南（英文）
├── 02_Supportive_Care/           # 支持性护理指南
├── 03_Patient_Guidelines_English/# 患者指南（英文）
├── 04_Clinical_Translations/     # 临床指南中文翻译
├── 05_Patient_Translations/      # 患者指南中文翻译
├── 06_Chinese_Patient_Guidelines/# 患者指南中文版本
├── markdown/                     # MinerU/OCR 生成的 Markdown
├── rag/                          # RAG chunk JSONL
├── .cache/                       # 癌种列表缓存
└── logs/                         # 日志和统计报告
```

## 配置选项

### 环境变量
| 变量 | 说明 |
|------|------|
| `NCCN_AUTH_METHOD` | 认证方式：`cookie` 或 `username_password` |
| `NCCN_COOKIE` | Cookie字符串，优先级高于文件 |
| `NCCN_COOKIE_FILE` | Cookie文件路径 |
| `NCCN_USERNAME` / `NCCN_PASSWORD` | 用户名密码 |
| `NCCN_DOWNLOAD_DIR` | 下载根目录 |
| `MINERU_TOKEN` | MinerU extract 模式 token |
| `NCCN_MINERU_MODE` | `flash` 或 `extract` |
| `NCCN_MINERU_LANGUAGE` | MinerU 识别语言 |
| `NCCN_OCR_BACKEND` | `mineru` 或 `deepseek-ocr` |
| `SILICONFLOW_API_KEY` | SiliconFlow API Key（OCR + 翻译） |
| `SILICONFLOW_BASE_URL` | 默认 `https://api.siliconflow.cn/v1` |
| `SILICONFLOW_MODEL` | 翻译模型，默认 `glm-4.5-air` |
| `NCCN_DEEPSEEK_OCR_MODEL` | OCR模型，默认 `deepseek-ai/DeepSeek-OCR` |
| `NCCN_DEEPSEEK_OCR_MAX_PAGES` | PDF最大页数，`0` 表示全部 |
| `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL` | OpenAI 兼容翻译配置 |

## 本地配置文件

推荐复制模板后在本地填写，不要把真实 Cookie/API Key 发给 Agent 或提交到仓库：

```bash
cp .env.template .env
# 或
cp config.json.template config.json
```

`.env`、`config.json`、`extracted_cookies.txt` 已在 `.gitignore` 中排除。

## 测试

```bash
# 离线回归测试（42项）
python3 test_offline.py

# 语法检查
python3 -m py_compile download_NCCN_Guide_v2_menu.py ncd.py nccn_rag.py
```

## 版本更新

### v2.3.0 更新内容
- ✅ 完整 65 种癌种列表（从 NCCN 官网提取，含中英文别名）
- ✅ 中文关键词自动扩展为英文别名（"胰腺" → "pancreatic, pancreas, 胰腺癌, 胰腺"）
- ✅ 二级菜单：语言筛选 + 癌种筛选
- ✅ PDF 清单选择：解析后展示编号列表，支持 `1,3,5-8` 格式
- ✅ 默认语言改为英文
- ✅ 癌种列表从 URL basename 改为锚文本提取（修复 "guidelines detail" bug）
- ✅ 患者指南双语/多语言解析恢复
- ✅ 主菜单恢复为 1-8 平铺结构

### v2.2.0
- ✅ `ncd` CLI 命令行工具
- ✅ MinerU / DeepSeek-OCR PDF 转 Markdown
- ✅ RAG chunk JSONL 生成
- ✅ SiliconFlow `glm-4.5-air` 翻译默认配置
- ✅ 安全本地配置（`.env.template` / `config.json.template`）

### v2.0.0
- ✅ 菜单式操作界面
- ✅ 6种主题下载
- ✅ 双重认证（用户名密码 + Cookie）
- ✅ 请求频率控制 + 错误重试
- ✅ 完善日志和统计系统
- ✅ 文件完整性验证

## 技术支持

### 获取帮助
- 查看日志文件：`tail -f nccn_downloads/logs/download_$(date +%Y%m%d).log`
- 确认网络连接和认证信息
- 验证 NCCN 网站可访问性

### 报告问题
请提供以下信息：
- 操作系统和 Python 版本
- 完整的错误日志
- 认证方式和使用步骤
- NCCN 网站访问状态

## 许可证

本工具仅供学习和研究使用，请遵守 NCCN 网站的使用条款。

---

**感谢使用 NCCN 指南下载工具 v2.3!**
感谢小x宝社区志愿者用❤️发电。
