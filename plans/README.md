# 修复计划索引

基准 commit: `5a7eabb9db2bd1f5d44542d1d9dbe35ccf0c5c89` (main 分支)

## 修复状态总览

| # | 问题 | 状态 | 文件 |
|---|---|---|---|
| F1 | 凭证泄露在公开仓库 git 历史 | ⚠️ 需手动操作 | 001-credential-purge.md |
| F2 | requests 调用缺 timeout | ✅ 已修复 | download_NCCN_Guide_v2_menu.py |
| F3 | 成功率统计虚高 | ✅ 已修复 | download_NCCN_Guide_v2_menu.py |
| F4 | 重复方法死代码 | ✅ 已修复 | download_NCCN_Guide_v2_menu.py |
| F5/F6 | 裸 except 与语义反转 | ✅ 已修复 | download_NCCN_Guide_v2_menu.py |
| F7 | 中文 PDF 语言识别 bug | ✅ 已修复 | download_NCCN_Guide_v2_menu.py |
| F8 | config download_settings 不被读取 | ✅ 已修复 | download_NCCN_Guide_v2_menu.py |
| F9 | ensure_authenticated 不检查 status_code | ✅ 已修复 | download_NCCN_Guide_v2_menu.py |
| F10 | retry 匹配逻辑错误 | ✅ 已修复 | download_NCCN_Guide_v2_menu.py |
| F13 | URL 无域名白名单 | ✅ 已修复 | download_NCCN_Guide_v2_menu.py |
| F12 | 无 requirements.txt / 无测试 | ✅ 已添加 | requirements.txt, test_offline.py |

## 依赖顺序

- F12 (requirements.txt + 离线测试) → 所有其他修复可由测试回归验证
- F1 (凭证清史) 需**手动执行**（不可由代码修复自动完成）

## 已排除的非问题

- 无 `verify=False` / 无明文 HTTP → TLS 校验默认开启 ✅
- 文件名清洗到位 → 无路径穿越 ✅
- 无并发 → 无竞态 ✅
