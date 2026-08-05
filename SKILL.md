---
name: skill-locator
description: 通用技能定位器。在用户级 WorkBuddy（~/.workbuddy/skills）、项目级（<workspace>/.workbuddy/skills，自动向上查找）、Codex（~/.codex/skills）等多处环境中查找指定技能的位置，解析 SKILL.md 元信息，输出统一结果（人读表格 / --json / --print-path）。当用户想知道某个技能装在哪里、是否被重复安装、或在脚本里拿到技能绝对路径时使用。零依赖、跨平台、无需任何配置即可直接调用。
version: 1.0.0
agent_created: true
---

# 通用技能定位器 skill-locator

一个可复用的定位模块：给定技能名（或名称片段），在多种运行环境里把它找出来，告诉你确切路径、属于哪个范围、SKILL.md 在不在。

解决的核心问题：技能可能散落在不同地方（用户级、项目级、Codex、自定义目录），手动翻路径既慢又容易漏。这个工具一次扫全，输出统一格式，别人拿到就能直接跑，不用改任何配置。

## 何时用

- 用户问「某某技能装在哪」「我是不是重复装了某个技能」「把这个技能的路径给我」。
- 需要在脚本 / CI 里拿到某个技能的绝对路径。
- 想确认技能在哪些范围生效（用户级还是项目级，还是 Codex 也有）。

## 怎么用

脚本在 `scripts/find_skill.py`，只用 Python 标准库，跨平台（macOS / Linux / Windows）。

查找（默认按名称包含匹配）：

```
python3 scripts/find_skill.py codex-session-brief
```

只做精确匹配：

```
python3 scripts/find_skill.py human-writing --exact
```

限定范围（all / user / project / codex）：

```
python3 scripts/find_skill.py arch --scope codex
```

只打印第一个匹配的绝对路径（方便管道）：

```
python3 scripts/find_skill.py my-skill --print-path
```

机器可读格式（脚本 / 自动化消费）：

```
python3 scripts/find_skill.py human --json
```

追加自定义技能根目录（可多次）：

```
python3 scripts/find_skill.py demo --extra-root /opt/skills --extra-root D:\skills
```

## 参数一览

- `query`（必填）：技能名称或名称片段
- `--exact`：只做精确名称匹配（大小写无关）
- `--scope {all|user|project|codex}`：限定搜索范围，默认 all
- `--workspace <路径>`：指定项目根目录，覆盖自动向上查找
- `--extra-root <路径>`：追加自定义技能根目录，可多次
- `--json`：输出 JSON（含 name / scope / path / skill_md / description / version）
- `--print-path`：只打印第一个匹配的绝对路径
- `--quiet`：仅输出路径，不打印说明

退出码：找到为 `0`，未找到为 `1`（便于在脚本里判断）。

## 设计要点（为什么别人能直接调用）

- 所有根目录都从 `$HOME` 与当前工作目录动态解析，不写死任何机器专属路径，换台电脑、换个系统照常跑。
- 路径解析统一走 `os.path`，Windows 的反斜杠、macOS/Linux 的正斜杠都不用手动处理。
- frontmatter 用内置轻量解析，不依赖 PyYAML 等第三方包，省去安装步骤。
- 输出三种形态（表格 / JSON / 单行路径），既能给人看，也能喂给其它程序。

## 输出示例（文本）

```
✓ 找到技能：codex-session-brief（2 处）

范围                 路径                                                   SKILL.md
------------------------------------------------------------------------------------------
Codex              /Users/li/.codex/skills/codex-session-brief          ✓
WorkBuddy 用户级      /Users/li/.workbuddy/skills/codex-session-brief      ✓
```
