#!/usr/bin/env python3
"""Render the shared scaffold into a CLI repo.

Usage: render.py <repo-dir>          write generated files
       render.py --check <repo-dir>  exit 1 if generated files drifted

Inputs live in <repo-dir>/.scaffold/: vars.json plus COMMANDS.md,
EXAMPLES.md and TCC.md snippets for the README. Only files listed in the
scaffold are written; repo-specific code (cmd/, internal/<pkg>/, skills/) is
never touched.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load(repo):
    with open(os.path.join(repo, ".scaffold", "vars.json"), encoding="utf-8") as f:
        v = json.load(f)
    for name in ("COMMANDS", "EXAMPLES", "TCC"):
        with open(os.path.join(repo, ".scaffold", name + ".md"), encoding="utf-8") as f:
            v[name] = f.read().strip()
    v["POLICY"] = "\n".join("   " + line for line in v["POLICY"].splitlines())
    v["MODULE"] = "github.com/Bam679/" + v["REPO"]
    return v


def subst(text, v):
    for k, val in v.items():
        if isinstance(val, str):
            text = text.replace("__" + k + "__", val)
    return text


def outputs(v):
    """Yield (relative target path, content, mode)."""
    repo_tpl = os.path.join(HERE, "repo")
    for dirpath, _, files in os.walk(repo_tpl):
        for fn in sorted(files):
            src = os.path.join(dirpath, fn)
            rel = os.path.relpath(src, repo_tpl)
            if rel == "README.md.tmpl":
                rel = "README.md"
            with open(src, encoding="utf-8") as f:
                content = subst(f.read(), v)
            yield rel, content, os.stat(src).st_mode & 0o777
    pkgs = ["agentcli"] + (["osa"] if v.get("APPLE") else [])
    for pkg in pkgs:
        base = os.path.join(HERE, "go", "internal", pkg)
        for dirpath, _, files in os.walk(base):
            for fn in sorted(files):
                src = os.path.join(dirpath, fn)
                rel = os.path.join("internal", pkg, os.path.relpath(src, base))
                with open(src, encoding="utf-8") as f:
                    content = f.read().replace("MODULE/", v["MODULE"] + "/")
                yield rel, content, 0o644
    adrs = ["0001-stack-and-shared-core.md", "0002-plugin-distribution.md", "0003-permission-model.md"]
    if v.get("APPLE"):
        adrs.append("0004-macos-bridge.md")
    for a in adrs:
        with open(os.path.join(ROOT, "docs", "adr", a), encoding="utf-8") as f:
            yield os.path.join("docs", "adr", a), f.read(), 0o644


def main(argv):
    check = "--check" in argv
    args = [a for a in argv if a != "--check"]
    if len(args) != 1:
        print(__doc__)
        return 2
    repo = os.path.abspath(args[0])
    v = load(repo)
    drift = []
    for rel, content, mode in outputs(v):
        dst = os.path.join(repo, rel)
        if check:
            try:
                with open(dst, encoding="utf-8") as f:
                    if f.read() != content:
                        drift.append(rel)
            except FileNotFoundError:
                drift.append(rel)
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(dst, mode)
    if check:
        if drift:
            print("scaffold drift in: " + ", ".join(sorted(drift)))
            return 1
        print("no scaffold drift")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
