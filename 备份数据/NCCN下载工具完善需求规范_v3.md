# NCCN下载工具完善需求规范 v3.0
## 基于v2.0开发经验的问题预防文档

---

## 📋 项目概述

本文档基于v2.0开发过程中遇到的问题和修复经验，制定了完善的需求规范，旨在避免在未来开发中出现类似的技术问题和不必要的重复修复工作。

---

## 🎯 核心功能需求

### 1. 菜单式下载系统
- **主菜单结构**: 支持6个主题选项 + 统计功能
- **增量下载**: 避免重复下载已存在的文件
- **目录管理**: 自动创建和维护主题分类目录
- **错误处理**: 优雅处理网络错误和认证失败

### 2. 认证系统
- **双重认证方式**:
  - 用户名/密码登录
  - Cookie文件登录
- **认证验证**: 启动时自动验证认证有效性
- **会话管理**: 维护有效的会话状态

### 3. 主题分类系统

#### 主题1: 癌症治疗指南英文版 (Treatment by Cancer Type - English Only)
- **URL**: https://www.nccn.org/guidelines/category_1
- **目录**: `01_Cancer_Treatment/`
- **语言过滤**: **仅英文版本**，过滤所有其他语言
- **内容过滤**: **仅Guidelines部分**，忽略附加文件
- **文件名格式**: `{癌种简称}_version_{版本号}.pdf`

#### 主题2: 支持性护理指南 (Supportive Care)
- **URL**: https://www.nccn.org/guidelines/category_3
- **目录**: `02_Supportive_Care/`
- **语言过滤**: 英文 + 中文版本
- **文件过滤**: **严格过滤** - Spanish版本、Framework文件、地区性文件
- **文件名格式**: `{原始文件名}_version_{版本号}.pdf`

#### 主题3: 患者指南英文版 (Patient Guidelines - English Only)
- **URL**: https://www.nccn.org/patientresources/patient-resources/guidelines-for-patients
- **目录**: `03_Patient_Guidelines_English/`
- **语言过滤**: **仅英文版本**
- **文件名格式**: `{癌种名}-patient.pdf`

#### 主题4: 临床指南中文翻译 (Clinical Translations)
- **URL**: https://www.nccn.org/global/what-we-do/clinical-guidelines-translations
- **目录**: `04_Clinical_Translations/`
- **语言过滤**: **仅中文版本**
- **文件名格式**: `{指南名}_chinese.pdf`

#### 主题5: 患者指南中文翻译 (Patient Guidelines Translations)
- **URL**: https://www.nccn.org/global/what-we-do/guidelines-for-patients-translations
- **目录**: `05_Patient_Translations/`
- **语言过滤**: **仅中文版本**
- **文件名格式**: `{癌种名}-zh-patient.pdf`

#### 主题6: 患者指南中文版本 (Chinese Patient Guidelines)
- **URL**: 从患者指南主页获取中文版本
- **目录**: `06_Chinese_Patient_Guidelines/`
- **语言过滤**: **仅中文版本**
- **文件名格式**: `{癌种名}-zh-patient.pdf`

---

## 🔧 技术规范要求

### 1. 文件名生成规范
**严格遵循以下命名规则**:

```python
def generate_filename(theme_type, title, version_info, pdf_url):
    """
    主题1 (癌症治疗): cancer_name_version_1_2026.pdf
    主题2 (支持性护理): original_name_version_1_2026.pdf
    主题3 (患者指南): cancer_name-patient.pdf
    主题4 (临床翻译): guideline_name_chinese.pdf
    主题5 (患者翻译): cancer_name-zh-patient.pdf
    主题6 (中文版): cancer_name-zh-patient.pdf
    """
```

**关键要求**:
- ✅ **主题1**: 从PDF URL提取癌种简称 (如: `cll`, `aml`)
- ✅ **主题2**: 保持原始文件名结构 (如: `fatigue`, `pain`)
- ✅ **主题3-6**: 遵循既定命名模式
- ❌ **禁止**: 生成通用名称如 `NCCN_Guideline_version_x_x.pdf`

### 2. 内容过滤规范

#### 必须过滤的文件类型
```python
EXCLUDE_PATTERNS = [
    # 会议和展览相关
    'exhibitor',      # 会议参展商手册
    'conference',     # 会议相关文件
    'prospectus',     # 招股说明书

    # 用户指南和模板
    'user guide',     # 用户指南
    'order template', # 订单模板

    # 框架文件
    'framework',      # Basic Framework, Core Framework等

    # 地区性文件
    'middle east',    # 中东地区
    'north africa',   # 北非
    'sub-saharan africa', # 撒哈拉以南非洲
    'mena',           # 中东北非地区

    # 多语言文件 (除主题2外)
    'spanish',        # 西班牙语
    'arabic',         # 阿拉伯语
    'hindi',          # 印地语
    'portuguese',     # 葡萄牙语
]
```

#### 必须保留的文件类型
```python
INCLUDE_PATTERNS = [
    'guidelines',     # 核心指南文件
    'nCCN',          # NCCN官方指南
]
```

### 3. 语言过滤规范

| 主题 | 英文版本 | 中文版本 | Spanish | 其他语言 |
|------|---------|---------|---------|----------|
| 主题1 | ✅ 仅此 | ❌ 过滤 | ❌ 过滤 | ❌ 过滤 |
| 主题2 | ✅ 保留 | ✅ 保留 | ❌ 过滤 | ❌ 过滤 |
| 主题3 | ✅ 仅此 | ❌ 过滤 | ❌ 过滤 | ❌ 过滤 |
| 主题4 | ❌ 过滤 | ✅ 仅此 | ❌ 过滤 | ❌ 过滤 |
| 主题5 | ❌ 过滤 | ✅ 仅此 | ❌ 过滤 | ❌ 过滤 |
| 主题6 | ❌ 过滤 | ✅ 仅此 | ❌ 过滤 | ❌ 过滤 |

### 4. 页面解析规范

#### URL拼接规则
```python
# 主题1: 癌症治疗指南
base_url = "https://www.nccn.org/guidelines/guidelines-detail?category=1&id={cancer_id}"

# 主题3: 患者指南
base_url = "https://www.nccn.org/patientresources/patient-resources/guidelines-for-patients/guidelines-for-patients-details?patientGuidelineId={patient_id}"

# PDF链接拼接
pdf_base = "https://www.nccn.org"
pdf_url = pdf_base + extracted_link
```

#### 内容提取规则
```python
# 仅提取Guidelines部分
guidelines_section = soup.find('h4', class_='GL')
if guidelines_section:
    pdf_links = extract_pdf_links_from_section(guidelines_section)
```

---

## ⚠️ 常见错误预防

### 1. 模块导入错误
**问题**: `local variable 're' referenced before assignment`
**预防**:
```python
# ✅ 正确: 全局导入
import re
import os
from urllib.parse import urlparse

class NCCNDownloader:
    def method_using_re(self):
        # 直接使用已导入的re模块
        pattern = re.compile(r'pattern')
        return pattern.search(text)

    # ❌ 错误: 函数内重复导入
    def method_using_re(self):
        import re  # 不要这样做！
        pattern = re.compile(r'pattern')
```

### 2. 文件名生成错误
**问题**: 生成通用文件名而非具体名称
**预防**:
```python
# ✅ 正确: 从URL提取原始文件名
def _enhance_pdf_info(self, title, version_info, pdf_url):
    if pdf_url:
        parsed_url = urlparse(pdf_url)
        filename = os.path.basename(parsed_url.path)
        filename_prefix = os.path.splitext(filename)[0]
        return f"{filename_prefix}_version_{version_info}.pdf"

    # 备选方案: 从title提取
    clean_title = re.sub(r'[^\w\-_]', '_', title)
    return f"{clean_title}_version_{version_info}.pdf"
```

### 3. 过滤逻辑不完整
**问题**: 下载了不需要的文件
**预防**:
```python
# ✅ 正确: 多重过滤检查
def _should_include_pdf(self, url, text):
    # 1. 检查排除模式
    if any(pattern in (url + text).lower() for pattern in self.EXCLUDE_PATTERNS):
        return False

    # 2. 检查主题特定规则
    if self.theme_type == '1':  # 癌症治疗
        if not self._is_english_only(url, text):
            return False
        if not self._is_guidelines_only(url, text):
            return False

    return True
```

---

## 🧪 测试规范

### 1. 单元测试要求
**每个功能模块必须包含测试**:
```python
# 文件名生成测试
def test_filename_generation():
    assert generate_filename('1', 'CLL Guidelines', '1_2026', '/pdf/cll.pdf') == 'cll_version_1_2026.pdf'

# 过滤逻辑测试
def test_filtering_logic():
    assert should_include_pdf('spanish_version.pdf', 'Spanish') == False
    assert should_include_pdf('cll_guidelines.pdf', 'English') == True

# 语言检测测试
def test_language_detection():
    assert detect_language('chinese_version.pdf') == 'chinese'
    assert detect_language('english_version.pdf') == 'english'
```

### 2. 集成测试要求
**每个主题必须通过完整的端到端测试**:
- 认证流程测试
- 页面解析测试
- 文件下载测试
- 文件命名验证测试
- 过滤逻辑验证测试

### 3. 兼容性测试要求
**确保修改不影响其他功能**:
```python
def test_cross_theme_compatibility():
    """确保主题间的修改不会相互影响"""
    for theme in ['1', '2', '3', '4', '5', '6']:
        result = test_theme_functionality(theme)
        assert result.success == True, f"Theme {theme} compatibility failed"
```

---

## 📊 质量检查清单

### 开发前检查
- [ ] 明确各主题的语言过滤需求
- [ ] 确定文件命名规范
- [ ] 定义必须过滤的文件类型
- [ ] 制定页面解析策略
- [ ] 设计测试用例

### 开发中检查
- [ ] 实现渐进式开发，逐一测试
- [ ] 保持向后兼容性
- [ ] 遵循现有代码风格
- [ ] 添加必要的错误处理
- [ ] 记录关键决策

### 开发后检查
- [ ] 运行所有单元测试
- [ ] 执行端到端测试
- [ ] 验证跨主题兼容性
- [ ] 检查文件命名正确性
- [ ] 确认过滤逻辑完整性

---

## 🚀 性能优化要求

### 1. 网络优化
- **重试机制**: 网络失败自动重试3次
- **并发控制**: 限制并发下载数量避免服务器压力
- **断点续传**: 支持大文件的断点续传

### 2. 存储优化
- **增量下载**: 检查文件存在性避免重复下载
- **文件去重**: 基于URL和文件大小去重
- **目录结构**: 清晰的分类目录结构

### 3. 用户体验优化
- **进度显示**: 实时显示下载进度
- **错误提示**: 清晰的错误信息和解决建议
- **统计信息**: 下载完成后的详细统计

---

## 📝 文档要求

### 1. 代码文档
- **函数文档**: 每个公共方法必须有docstring
- **类型注解**: 使用类型注解明确参数和返回值类型
- **注释**: 复杂逻辑必须有行内注释

### 2. 用户文档
- **使用说明**: 详细的使用步骤说明
- **故障排除**: 常见问题和解决方案
- **配置说明**: 各配置选项的详细说明

### 3. 开发文档
- **架构设计**: 系统架构和设计决策
- **API文档**: 内部API接口文档
- **测试文档**: 测试策略和测试用例说明

---

## 🎯 验收标准

### 功能验收
- [ ] 所有6个主题都能正确下载对应文件
- [ ] 文件命名完全符合规范要求
- [ ] 语言过滤准确无误
- [ ] 内容过滤精确有效
- [ ] 错误处理完善

### 性能验收
- [ ] 大文件下载稳定
- [ ] 网络异常自动恢复
- [ ] 内存使用合理
- [ ] 下载速度可接受

### 质量验收
- [ ] 代码覆盖率 > 80%
- [ ] 无已知严重bug
- [ ] 兼容性测试全部通过
- [ ] 文档完整准确

---

## 📚 参考资源

### 配置文件
- `config.json` - 主配置文件
- `themes_config.py` - 主题配置模块

### 测试文件
- `test_*.py` - 各类功能测试文件
- `compatibility_test.py` - 兼容性测试

### 工具脚本
- `debug_*.py` - 调试工具
- `analysis_*.py` - 分析工具

---

**总结**: 本规范文档基于v2.0开发过程中的真实问题和解决方案制定，旨在为v3.0开发提供清晰的指导，避免重复犯同样的错误，确保开发质量和用户体验。