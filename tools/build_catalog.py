#!/usr/bin/env python3
"""Build catalog.json from apps/*/app.json, or check that it is up to date.

    python3 tools/build_catalog.py          # write catalog.json
    python3 tools/build_catalog.py --check  # fail if catalog.json is out of date (CI)

Each app lives in apps/<id>/app.json. MeshHome reads catalog.json, fetches each recipe from beside
it, and only uses a recipe whose SHA-256 matches the one listed here.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog.json"


def build() -> str:
    apps = []
    for path in sorted((ROOT / "apps").glob("*/app.json")):
        raw = path.read_bytes()
        recipe = json.loads(raw)
        folder = path.parent.name
        if recipe.get("id") != folder:
            sys.exit(f"{path}: id {recipe.get('id')!r} must match its folder {folder!r}")
        if not re.fullmatch(r"\d+\.\d+\.\d+", str(recipe.get("version", ""))):
            sys.exit(f"{path}: version must look like 1.2.3")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 &/+-]{0,29}", str(recipe.get("category", ""))):
            sys.exit(f"{path}: needs a category (up to 30 characters, e.g. \"Weather\")")
        entry = {
            "id": recipe["id"],
            "name": recipe["name"],
            "version": recipe["version"],
            "category": recipe["category"],
            "summary": recipe["summary"],
            "recipe": f"apps/{folder}/app.json",
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
        if recipe.get("min_meshhome"):
            entry["min_meshhome"] = recipe["min_meshhome"]
        apps.append(entry)
    return json.dumps({"schema": 1, "apps": apps}, indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    text = build()
    if "--check" in sys.argv:
        if not CATALOG.exists() or CATALOG.read_text() != text:
            sys.exit("catalog.json is out of date: run python3 tools/build_catalog.py and commit it")
        print("catalog.json is up to date")
    else:
        CATALOG.write_text(text)
        print(f"wrote {CATALOG.name} ({len(json.loads(text)['apps'])} apps)")
