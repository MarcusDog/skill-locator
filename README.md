# skill-locator

通用技能（skill）定位器。给定技能名或名称片段，在多种运行环境里把它找出来，告诉你确切路径、所属范围，并解析 `SKILL.md` 的元信息，输出统一结果。

## 为什么需要它

技能可能散落在不同地方：

- 用户级 WorkBuddy：`~/.workbuddy/skills/<name>/`
- 项目级 WorkBuddy：`<workspace>/.workbuddy/skills/<name>/`（自动从当前目录向上查找）
- Codex：`~/.codex/skills/<name>/`
- 任意自定义目录（`--extra-root`）

手动翻路径既慢又容易漏，尤其当同一个技能被装了多处时。这个工具一次扫全，格式统一，别人拿到就能直接跑。

## 特性

- **零依赖**：只用 Python 标准库，无需 `pip install`
- **跨平台**：macOS / Linux / Windows 通吃，路径解析走 `os.path`
- **零配置**：根目录从 `$HOME` 与当前工作目录动态解析，不写死任何机器路径
- **三种输出**：人读表格、`--json` 机器格式、`--print-path` 单行路径
- **退出码**：找到 `0`，未找到 `1`，方便在脚本 / CI 里判断

## 安装

直接把整个 `skill-locator` 目录放进任意技能目录即可，例如：

```bash
# WorkBuddy 用户级
cp -r skill-locator ~/.workbuddy/skills/

# Codex
cp -r skill-locator ~/.codex/skills/
```

## 用法

```bash
# 按名称包含匹配（默认）
python3 scripts/find_skill.py codex-session-brief

# 精确匹配
python3 scripts/find_skill.py human-writing --exact

# 限定范围
python3 scripts/find_skill.py arch --scope codex

# 只打印第一个匹配的绝对路径（管道友好）
python3 scripts/find_skill.py my-skill --print-path

# 机器可读
python3 scripts/find_skill.py human --json

# 追加自定义根目录
python3 scripts/find_skill.py demo --extra-root /opt/skills --extra-root D:\skills
```

### 参数

| 参数 | 说明 |
| --- | --- |
| `query` | 技能名称或名称片段（必填） |
| `--exact` | 只做精确名称匹配（大小写无关） |
| `--scope` | `all` / `user` / `project` / `codex`，默认 `all` |
| `--workspace` | 指定项目根目录，覆盖自动向上查找 |
| `--extra-root` | 追加自定义技能根目录，可多次 |
| `--json` | 输出 JSON |
| `--print-path` | 只打印第一个匹配的绝对路径 |
| `--quiet` | 仅输出路径 |

## 输出示例

```text
✓ 找到技能：codex-session-brief（2 处）

范围                 路径                                                   SKILL.md
------------------------------------------------------------------------------------------
Codex              /Users/li/.codex/skills/codex-session-brief          ✓
WorkBuddy 用户级      /Users/li/.workbuddy/skills/codex-session-brief      ✓
```

`--json` 输出结构：

```json
{
  "query": "human",
  "found": 2,
  "results": [
    {
      "name": "human-writing",
      "scope": "WorkBuddy 用户级",
      "path": "/Users/li/.workbuddy/skills/human-writing",
      "skill_md": true,
      "description": "通用中文创作与改稿 Skill……",
      "version": ""
    }
  ]
}
```

## 目录结构

```
skill-locator/
├── SKILL.md              # 技能说明（供 WorkBuddy / Codex 发现）
├── README.md             # 本文件
├── scripts/
│   └── find_skill.py     # 定位脚本（零依赖）
└── references/           # 扩展说明（预留）
```

## License

MIT
