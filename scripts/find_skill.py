#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
find_skill.py — 通用技能定位器

在多种运行环境里查找某个技能（skill）的位置，输出统一结果。
技能可能散落在不同「范围（scope）」下，本工具无需任何配置即可用：
  用户级 WorkBuddy   ~/.workbuddy/skills/<name>/
  项目级 WorkBuddy   <workspace>/.workbuddy/skills/<name>/   （自动向上查找 cwd）
  Codex              ~/.codex/skills/<name>/
以及通过 --extra-root 追加的任意目录。

特性：
  - 零依赖，只用 Python 标准库
  - 跨平台（macOS / Linux / Windows），路径全部用 os.path 解析
  - 名称匹配支持「精确」与「包含」两种模式
  - 自动解析 SKILL.md 的 frontmatter（name / description / version）
  - 统一输出：人读表格、--json 机器格式、--print-path 单行路径
  - 退出码：找到为 0，未找到为 1（方便在其他脚本 / CI 里判断）

用法：
  python3 find_skill.py <技能名>
  python3 find_skill.py codex-session-brief
  python3 find_skill.py human-writing --json
  python3 find_skill.py arch --scope codex
  python3 find_skill.py my-skill --print-path
  python3 find_skill.py demo --extra-root /opt/skills --extra-root D:\\skills
"""

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# 技能根目录解析（动态、跨平台、零配置）
# ---------------------------------------------------------------------------

def default_roots():
    """返回系统里默认的技能根目录列表（绝对路径）。"""
    home = os.path.expanduser("~")
    roots = [
        (os.path.join(home, ".workbuddy", "skills"), "WorkBuddy 用户级"),
        (os.path.join(home, ".codex", "skills"), "Codex"),
    ]
    return roots


def detect_project_root(start=None):
    """从 start（默认 cwd）向上查找第一个含 .workbuddy/skills 的目录。"""
    cur = os.path.abspath(start or os.getcwd())
    # 最多向上 8 层，避免无限循环
    for _ in range(8):
        cand = os.path.join(cur, ".workbuddy", "skills")
        if os.path.isdir(cand):
            return cand
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return None


def collect_roots(args):
    """按参数汇总所有要搜索的 (path, scope_label)。"""
    roots = []
    seen = set()

    def add(path, label):
        ap = os.path.abspath(path)
        if ap in seen:
            return
        seen.add(ap)
        roots.append((ap, label))

    if args.scope in ("all", "user"):
        for p, label in default_roots():
            if "WorkBuddy 用户级" in label:
                add(p, label)
    if args.scope in ("all", "codex"):
        for p, label in default_roots():
            if label == "Codex":
                add(p, label)
    if args.scope in ("all", "project"):
        if args.workspace:
            add(os.path.join(args.workspace, ".workbuddy", "skills"),
                "WorkBuddy 项目级")
        else:
            pr = detect_project_root()
            if pr:
                add(pr, "WorkBuddy 项目级")
    for extra in args.extra_root or []:
        add(extra, "自定义")

    return roots


# ---------------------------------------------------------------------------
# SKILL.md frontmatter 解析（轻量，不引入 PyYAML）
# ---------------------------------------------------------------------------

def parse_frontmatter(path):
    """读取 SKILL.md 的 YAML frontmatter，返回 dict（仅支持简单 key: value）。"""
    meta = {}
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return meta
    if not lines or lines[0].strip() != "---":
        return meta
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip()
        if key:
            meta[key] = val
    return meta


# ---------------------------------------------------------------------------
# 查找逻辑
# ---------------------------------------------------------------------------

def find_skills(query, roots, exact=False):
    """在所有 roots 下查找技能目录，返回匹配列表。"""
    results = []
    q = query.lower()
    for root, scope in roots:
        if not os.path.isdir(root):
            continue
        try:
            entries = os.listdir(root)
        except OSError:
            continue
        for name in entries:
            d = os.path.join(root, name)
            if not os.path.isdir(d):
                continue
            nl = name.lower()
            if exact:
                if nl != q:
                    continue
            else:
                if q not in nl:
                    continue
            skill_md = os.path.join(d, "SKILL.md")
            meta = parse_frontmatter(skill_md) if os.path.isfile(skill_md) else {}
            results.append({
                "name": name,
                "scope": scope,
                "path": os.path.abspath(d),
                "skill_md": os.path.isfile(skill_md),
                "description": meta.get("description", ""),
                "version": meta.get("version", ""),
            })
    # 同名技能，用户级优先；其余按范围名字排序，结果稳定
    results.sort(key=lambda r: (r["name"], r["scope"]))
    return results


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------

def print_table(results, query):
    if not results:
        print(f"✗ 未找到技能：{query}")
        print("提示：换更短的关键词，或用 --scope / --extra-root 扩大搜索范围。")
        return
    print(f"✓ 找到技能：{query}（{len(results)} 处）\n")
    print(f"{'范围':<18} {'路径':<52} {'SKILL.md'}")
    print("-" * 90)
    for r in results:
        print(f"{r['scope']:<18} {r['path']:<52} {'✓' if r['skill_md'] else '—'}")
    descs = [r["description"] for r in results if r["description"]]
    if descs:
        print("\n描述：")
        for d in descs[:3]:
            print(f"  {d[:120]}{'…' if len(d) > 120 else ''}")


def main():
    parser = argparse.ArgumentParser(
        description="通用技能定位器：在多种环境里查找技能位置并输出统一结果。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("query", help="技能名称或名称片段（默认按包含匹配）")
    parser.add_argument("--exact", action="store_true",
                        help="只做精确名称匹配（区分大小写无关）")
    parser.add_argument("--scope", choices=["all", "user", "project", "codex"],
                        default="all", help="限定搜索范围（默认 all）")
    parser.add_argument("--workspace", help="指定项目根目录（覆盖自动向上查找）")
    parser.add_argument("--extra-root", action="append", default=[],
                        help="追加自定义技能根目录（可多次使用）")
    parser.add_argument("--json", action="store_true", help="输出 JSON 机器格式")
    parser.add_argument("--print-path", action="store_true",
                        help="只打印第一个匹配的绝对路径（便于管道使用）")
    parser.add_argument("--quiet", action="store_true", help="仅输出结果，不打印说明")
    args = parser.parse_args()

    roots = collect_roots(args)
    results = find_skills(args.query, roots, exact=args.exact)

    if args.json:
        print(json.dumps({"query": args.query, "found": len(results),
                          "results": results}, ensure_ascii=False, indent=2))
        sys.exit(0 if results else 1)

    if args.print_path:
        if results:
            print(results[0]["path"])
            sys.exit(0)
        sys.exit(1)

    if not args.quiet:
        print_table(results, args.query)
    else:
        for r in results:
            print(r["path"])
    sys.exit(0 if results else 1)


if __name__ == "__main__":
    main()
