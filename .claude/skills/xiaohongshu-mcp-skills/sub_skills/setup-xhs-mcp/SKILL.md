---
name: setup-xhs-mcp
description: |
  安装部署 xiaohongshu-mcp 服务并验证 MCP 连接，引导用户完成从零到可用的全流程。
  当用户第一次使用小红书功能、提到安装/部署/配置小红书、环境搭建、MCP 服务连接失败、
  或 check_login_status 等 MCP 工具不可用时使用。
---

项目仓库：https://github.com/xpzouying/xiaohongshu-mcp

## 执行流程

### 1. 检测服务状态

检查 xiaohongshu-mcp 是否已在运行：

```bash
/usr/bin/curl -so /dev/null -w "%{http_code}" http://localhost:18060/mcp 2>/dev/null
```

- 返回 HTTP 状态码（如 405、200）→ 服务已运行，跳到步骤 4
- 返回空或连接拒绝 → 询问用户：MCP 服务未找到，是没安装过还是服务停了？
  - 没安装过（或已删除）→ 步骤 2
  - 安装了但未运行 → 步骤 3

### 2. 部署服务（下载代码）

先检查 Go 是否安装：

```bash
go version 2>/dev/null || echo "NOT_INSTALLED"
```

如果输出 `NOT_INSTALLED`，引导用户安装 Go：`brew install go`，安装完再继续。

从 GitHub Releases 下载最新版本（全部使用 curl，macOS 原生支持）：

```bash
repo_name="xpzouying/xiaohongshu-mcp"

get_latest_release() {
  /usr/bin/curl --silent "https://api.github.com/repos/$1/releases/latest" |
    grep '"tag_name":' |
    sed -E 's/.*"([^"]+)".*/\1/'
}

LATEST=$(get_latest_release "${repo_name}")
echo $LATEST
VER=$(echo "$LATEST" | cut -c2-)
echo "${repo_name} latest version is ${VER}"

# 下载并解压到 mcps/xiaohongshu-mcp
mkdir -p mcps
cd mcps
mkdir -p xiaohongshu-mcp
/usr/bin/curl -L "https://github.com/${repo_name}/archive/refs/tags/${LATEST}.tar.gz" -o /tmp/xhs-mcp.tar.gz
tar xzvf /tmp/xhs-mcp.tar.gz -C xiaohongshu-mcp --strip-components=1
rm -f /tmp/xhs-mcp.tar.gz
```

### 3. 启动 MCP 服务

新建终端，在后台启动服务：

```bash
cd mcps/xiaohongshu-mcp
go run .
```

验证服务是否正常响应：
```bash
/usr/bin/curl -s -X POST http://localhost:18060/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}'
```

服务运行在 `http://localhost:18060/mcp`。

### 4. 登录小红书

引导用户使用 [xhs-login](../xhs-login/SKILL.md) 子技能完成扫码登录。


## 失败处理

| 场景 | 处理 |
|---|---|
| 端口 18060 被占用 | 检查已有进程：`lsof -i :18060`，或终止旧进程后重启 |
| Go 未安装 | 引导用户先安装 Go：`brew install go` |
| 下载失败 | 检查网络，或手动指定版本号下载 |
