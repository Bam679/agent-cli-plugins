#!/bin/sh
# Pin a CLI plugin in the marketplace to a released tag: scripts/bump.sh apple-mail v0.2.0
set -eu
name=$1; ref=$2
case "$ref" in v[0-9]*.[0-9]*.[0-9]*) ;; *) echo "ref must look like vX.Y.Z"; exit 2 ;; esac
python3 - "$name" "$ref" <<'PY'
import json, sys
name, ref = sys.argv[1], sys.argv[2]
p = ".claude-plugin/marketplace.json"
m = json.load(open(p))
hit = [x for x in m["plugins"] if x["name"] == name and isinstance(x["source"], dict)]
if not hit: sys.exit("no such git plugin: " + name)
hit[0]["source"]["ref"] = ref
open(p, "w").write(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
PY
echo "$name -> $ref"
