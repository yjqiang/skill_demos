---
name: xhs-login
description: |
  管理小红书登录状态：检查是否已登录、二维码扫码登录、重置登录切换账号。
  当用户提到登录、扫码、账号、切换账号、退出登录、登录状态检查，
  或其他子技能报告"未登录"需要先登录时使用。
---

## 执行流程

### 1. 检查登录状态

调用 `check_login_status`（无参数），返回是否已登录及当前用户名。

- 已登录 → 告知用户当前登录账号
- 未登录 → 进入步骤 2

### 2. 扫码登录

调用 `get_login_qrcode`（无参数）。MCP 工具返回两部分：
- 文本：超时提示（含截止时间）
- 图片：PNG 格式二维码（MCP image content type，Base64 编码）

**展示二维码**：MCP 返回的图片会通过客户端渲染。如果客户端无法直接展示
图片（如纯文本终端），将 MCP 响应通过 JSON 解析后保存为临时 PNG 然后打开。

**重要：不要手动复制 base64 字符串！** 超长 base64 在手抄过程中必然截断/混入空白字符，
导致图片损坏（一片空白）。正确做法是先把完整 JSON 响应写入文件，再用
`json.load()` + `base64.b64decode()` 提取解码。

```bash
# 先决条件：如果用户指定了 Python 路径，用该 Python，否则用 python3
# 本示例用 PYTHON 变量，执行时替换为用户指定的路径或 python3

# Step 1: 将 MCP 工具返回的完整 JSON 响应保存到临时文件
# （curl 调用 get_login_qrcode 时，用 -o /tmp/xhs-qrcode-resp.json 或重定向 >）

# Step 2: 用 json.load 安全提取 base64 数据，解码写入文件
$PYTHON -c "
import json, base64
with open('/tmp/xhs-qrcode-resp.json') as f:
    resp = json.load(f)
for item in resp['result']['content']:
    if item.get('type') == 'image':
        img_bytes = base64.b64decode(item['data'])
        with open('/tmp/xhs-qrcode.png', 'wb') as out:
            out.write(img_bytes)
        print(f'{len(img_bytes)} bytes -> /tmp/xhs-qrcode.png')
    elif item.get('type') == 'text':
        print(item['text'])
"

# Step 3: 打开图片。
open /tmp/xhs-qrcode.png   # macOS
```

提示用户：
- 打开小红书 App 扫描二维码
- 二维码有效期有限（通常 5 分钟），过期需重新获取

扫码完成后，再次调用 `check_login_status` 确认登录成功。

## 约束

- 登录需要用户手动用手机 App 扫码，无法自动完成
- 单次扫码有效期约 5 分钟，超时需重新调用 `get_login_qrcode`
- MCP 会话由 Claude Code 自动管理，无需手动处理 session ID

## 失败处理

| 场景                       | 处理 |
|--------------------------|---|
| MCP 工具不可用或者找不到 MCP 服务器地址 | 引导用户使用 [setup-xhs-mcp](../setup-xhs-mcp/SKILL.md) 子技能部署和连接 |
| 二维码超时                    | 重新调用 `get_login_qrcode` |
| 扫码后仍显示未登录                | 等待几秒后重新 `check_login_status`，可能扫码成功但状态同步有延迟 |
