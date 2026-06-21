# 小红书 Skills 项目

三个 Claude Code Skill 组成的小红书内容生产工具链，按职责分三层：

```
🛠️ 平台操作                ✍️ 洗稿                    🎬 编排
xiaohongshu-mcp-skills    xhs-editor-pipeline       xhs-content-factory
```

---

## 1. xiaohongshu-mcp-skills — 平台操作

基于 [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) MCP 服务的小红书自动化助手。

```
SKILL.md                 ← 总入口，意图识别 & 路由
sub_skills/
├── setup-xhs-mcp/       ← 安装部署 MCP 服务
├── xhs-login/           ← 扫码登录 & 会话管理
└── xhs-explore/         ← 浏览推荐流 & 笔记详情
```

总入口只做路由，子技能各司其职，问题自动联动（浏览时未登录 → 引导登录）。

---

## 2. xhs-editor-pipeline — 洗稿改写

按「毒舌搞钱学姐」人设洗稿——**保留信息骨架，换掉表达皮囊**。

```
SKILL.md                      ← 洗稿主流程
references/guidelines.md      ← 人设：语气、高频词、emoji 规范
templates/
├── ads.md                    ← 好物种草类模板
└── share_ideas.md            ← 观点分享类模板（按需只加载一个）
scripts/final_check_and_rewrite.py  ← 后处理：敏感词、emoji、排版
```

流程：加载人设 → 按类型加载模板 → LLM 改写 → 脚本后处理。

---

## 3. xhs-content-factory — 编排调度

端到端流水线，串联上面两个 Skill：**刷推荐 → 选内容 → 洗稿出稿**。

```
SKILL.md                    ← 编排主流程（自己不实现逻辑，全委托给专项 Skill）
```

关键节点让用户确认，不会自作主张。

---

## 依赖

- **Claude Code** — Skill 运行平台
- **Go** — MCP 服务编译
- **Python 3 + pypinyin** — 洗稿后处理脚本
- **[xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)** — 底层 MCP 服务
