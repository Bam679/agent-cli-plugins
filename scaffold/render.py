#!/usr/bin/env python3
"""Render the shared scaffold into a CLI repo.

Usage: render.py <repo-dir>          write generated files
       render.py --check <repo-dir>  exit 1 if generated files drifted

Inputs live in <repo-dir>/.scaffold/: vars.json plus Markdown snippets
(COMMANDS, TCC, MECHANISM, MEASURED, QUICKSTART, HOW_IT_WORKS, WHEN_NOT,
TUTORIAL, REFERENCE and the optional ACKNOWLEDGMENTS) for the README and docs. Only files listed in the
scaffold are written; repo-specific code (cmd/, internal/<pkg>/, skills/) is
never touched.
"""
import json
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
# Written once when a repo is created; release-please maintains them later.
SEED_ONLY = {".release-please-manifest.json", os.path.join("plugin", ".claude-plugin", "plugin.json")}
ROOT = os.path.dirname(HERE)


def load(repo):
    with open(os.path.join(repo, ".scaffold", "vars.json"), encoding="utf-8") as f:
        v = json.load(f)
    for name in ("COMMANDS", "TCC", "MECHANISM", "MEASURED", "QUICKSTART", "HOW_IT_WORKS", "WHEN_NOT",
                 "TUTORIAL", "REFERENCE", "ACKNOWLEDGMENTS"):
        try:
            with open(os.path.join(repo, ".scaffold", name + ".md"), encoding="utf-8") as f:
                v[name] = f.read().strip()
        except FileNotFoundError:
            v[name] = ""
    if v["ACKNOWLEDGMENTS"]:
        v["ACKNOWLEDGMENTS"] = "\n## Acknowledgements\n\n" + v["ACKNOWLEDGMENTS"] + "\n"
    v["POLICY"] = "\n".join("   " + line for line in v["POLICY"].splitlines())
    v["MODULE"] = "github.com/Bam679/" + v["REPO"]
    v.setdefault("DEFAULT_ACCESS", "`" + v["BIN"] + "` only reads until you allow writes in")
    v.setdefault("DEFAULT_NOTE", "")
    return v


def icon_png(hex_color, size=512):
    """A deterministic plugin icon: a white ring on a coloured square."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    c, outer, inner = size / 2, size * 0.32, size * 0.20
    rows = []
    for y in range(size):
        row = bytearray(b"\x00")
        for x in range(size):
            d = ((x - c) ** 2 + (y - c) ** 2) ** 0.5
            row += bytes((255, 255, 255)) if inner <= d <= outer else bytes((r, g, b))
        rows.append(bytes(row))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b"")


def binaries(v):
    """Yield (relative path, bytes): plugin icon and logos from brand/<bin>/,
    or a generated icon when the brand folder has no assets."""
    brand = os.path.join(ROOT, "brand", v["BIN"])
    icon = os.path.join(brand, "icon-512.png")
    if os.path.exists(icon):
        with open(icon, "rb") as f:
            yield os.path.join("plugin", ".claude-plugin", "icon.png"), f.read()
        for name in ("logo.svg", "logo-dark.svg", "icon.svg"):
            with open(os.path.join(brand, name), "rb") as f:
                yield os.path.join("assets", name), f.read()
    else:
        yield os.path.join("plugin", ".claude-plugin", "icon.png"), icon_png(v.get("ICON_COLOR", "#3B5BDB"))


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
    for rel, data in binaries(v):
        dst = os.path.join(repo, rel)
        if check:
            try:
                with open(dst, "rb") as f:
                    if f.read() != data:
                        drift.append(rel)
            except FileNotFoundError:
                drift.append(rel)
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as f:
            f.write(data)
    for rel, content, mode in outputs(v):
        dst = os.path.join(repo, rel)
        if rel in SEED_ONLY and os.path.exists(dst):
            continue  # owned by release-please after the first render
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


def write_icon(path, color):
    with open(path, "wb") as f:
        f.write(icon_png(color))


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--icon":
        write_icon(sys.argv[2], sys.argv[3])
        sys.exit(0)
    sys.exit(main(sys.argv[1:]))
