# 如何获取NCCN网站Cookie指南

## 概述
NCCN下载工具支持使用Cookie进行认证，避免每次都要输入用户名密码。本指南详细说明如何获取和配置NCCN网站的Cookie。

## 方法一：浏览器开发者工具获取Cookie（推荐）

### 步骤1：登录NCCN网站
1. 打开浏览器，访问：https://www.nccn.org/
2. 点击右上角的"Log In"按钮
3. 输入您的NCCN用户名和密码
4. 成功登录后，确保保持登录状态

### 步骤2：获取Cookie
1. **Chrome浏览器**：
   - 按F12或右键→检查，打开开发者工具
   - 切换到"Application"（应用）标签页
   - 在左侧菜单中选择"Storage"→"Cookies"→"https://www.nccn.org"
   - 在右侧面板中查看所有Cookie
https://picgo-1302991947.cos.ap-guangzhou.myqcloud.com/images/20251101174057062.png



## 配置Cookie文件格式

### 提取的Cookie文件格式
```
ASP.NET_SessionId	abcd1234efgh5678ijkl9012mnop3456
NCCNAccount		user_sid_xyz789
AuthToken		auth_abcdef123456
```

### 配置文件设置
在 `config.json` 中配置Cookie认证：
```json
{
    "authentication": {
        "method": "cookie",
        "cookie_file": "extracted_cookies.txt"
    }
}
```

## 常见问题和解决方案

### 1. Cookie无效或过期
**问题**：运行程序时提示认证失败
**解决**：
- 重新访问NCCN网站确认登录状态
- 重新获取最新的Cookie
- 检查Cookie是否包含必要的认证信息

### 2. 获取的Cookie不完整
**问题**：Cookie文件只包含部分内容
**解决**：
- 确保在NCCN网站完全登录后再获取Cookie
- 尝试访问需要认证的页面后获取Cookie
- 检查浏览器是否阻止了第三方Cookie

### 3. Cookie格式问题
**问题**：程序无法读取Cookie文件
**解决**：
- 确保Cookie文件格式正确（每行一个Cookie，格式：name\tvalue）
- 检查文件编码为UTF-8
- 验证文件路径在config.json中配置正确

## 安全注意事项

### Cookie安全
1. **保护Cookie文件**：Cookie文件包含敏感信息，请妥善保管
2. **不要分享**：不要将Cookie文件分享给他人
3. **定期更新**：建议定期更新Cookie以确保安全性
4. **删除旧文件**：更新Cookie后删除旧的Cookie文件

### 最佳实践
1. **专用浏览器**：使用专门的浏览器配置文件获取Cookie
2. **隐私模式**：获取Cookie后清理浏览数据
3. **文件权限**：设置Cookie文件为只读权限（chmod 400）

## 故障排除

### 认证失败检查清单
- [ ] 确认NCCN账户有效且未过期
- [ ] 验证Cookie文件路径正确
- [ ] 检查Cookie文件格式
- [ ] 确认Cookie包含必要字段
- [ ] 尝试重新登录并获取新Cookie

### 日志分析
运行程序时开启详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 更新和维护

### 定期检查
- 每月检查Cookie有效性
- 关注NCCN网站是否有认证方式变更
- 及时更新获取方法

### 自动化更新
可以考虑设置定时任务自动更新Cookie：
```bash
# 每周一早上9点更新Cookie
0 9 * * 1 python update_nccn_cookie.py
```

---

**重要提醒**：Cookie认证方式方便但需要定期维护。如果遇到持续性问题，建议使用用户名密码认证方式。
