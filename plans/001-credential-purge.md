# F1: 凭证泄露清除计划

## 问题

真实 NCCN 账号密码（明文）和活跃会话 Cookie 已进入公开 GitHub 仓库的 git 历史：

- **仓库**: `github.com:PancrePal-xiaoyibao/NCCN_guideline_download.git`（公开，HTTP 200）
- **泄露文件**:
  - `config.json` — 含 NCCN 邮箱 + 明文密码，存在于 `58052a6`、`1c089ff`、`02fafc4`、`2b0ff06` 等提交
  - `extracted_cookies.txt` — 含 `.AspNet.Cookies`、`ASP.NET_SessionId`、`customerguid` 等，存在于 `58052a6`、`f3b1f73`、`3ef0a90`、`2b0ff06`、`02fafc4`、`1c089ff` 等提交
- **当前状态**: `.gitignore` 已排除这两个文件（不再新增），但历史中仍可恢复

## 必须手动执行的步骤（按顺序）

### 步骤 1: 立即轮换 NCCN 密码

> ⚠️ 这一步**必须最先做**。清史不能撤销"已公开暴露"的事实。

1. 登录 https://www.nccn.org 修改账户密码
2. 登出所有设备/会话，使已泄露的 Cookie 失效
3. 如果该密码用于其他网站，也一并修改

### 步骤 2: 从 config.json 中移除明文密码字段

代码已支持 Cookie 认证，`password` 字段是冗余的攻击面：

```json
{
  "authentication": {
    "method": "cookie",
    "cookie_file": "extracted_cookies.txt"
  },
  ...
}
```

### 步骤 3: 清除 git 历史

使用 `git filter-repo`（推荐）或 BFG Repo Cleaner：

```bash
# 安装 git-filter-repo
pip install git-filter-repo

# 从所有历史中删除敏感文件
git filter-repo --invert-paths --path config.json --path extracted_cookies.txt

# 强制推送到远程（会重写所有协作者的历史）
git push origin --force --all

# 如果有标签也需要更新
git push origin --force --tags
```

或者使用 BFG：

```bash
# 安装 BFG
brew install bfg  # macOS

# 删除文件
bfg --delete-files config.json
bfg --delete-files extracted_cookies.txt
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin --force --all
```

### 步骤 4: 通知协作者

所有已 clone 该仓库的人需要：

```bash
git fetch origin
git reset --hard origin/main
```

### 步骤 5: 验证

```bash
# 确认历史中不再包含敏感文件
git log --all --oneline -- config.json extracted_cookies.txt
# 应无输出

# 确认 GitHub 上搜索不到
# 访问 https://github.com/PancrePal-xiaoyibao/NCCN_guideline_download/search?q=password
```

## 风险

- 强推会重写历史，所有 fork/clone 需要重建
- 密码一旦公开就无法保证未被复制，轮换是唯一的根治
- 如果仓库已有 fork，fork 中的历史不会自动清除（需联系 fork 拥有者）

## 完成标准

- [ ] NCCN 密码已修改
- [ ] 旧会话 Cookie 已失效
- [ ] config.json 中无明文 password 字段
- [ ] git 历史中搜索 `config.json` / `extracted_cookies.txt` 无结果
- [ ] GitHub 仓库搜索无敏感内容
