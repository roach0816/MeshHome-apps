#!/usr/bin/env python3
"""Check every app with MeshHome's own recipe engine (the same checks MeshHome makes before
installing one).

    python3 tools/validate.py path/to/bot_recipes.py

CI downloads bot_recipes.py from MeshHome's main branch; it needs pydantic and httpx.
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location("bot_recipes", sys.argv[1])
engine = importlib.util.module_from_spec(spec)
sys.modules["bot_recipes"] = engine  # pydantic resolves the recipe types through it
spec.loader.exec_module(engine)

failed = False
for path in sorted((ROOT / "apps").glob("*/app.json")):
    try:
        recipe = engine.load(path.read_bytes())
        commands = ", ".join(f"/{c.name}" for c in recipe.commands)
        print(f"ok   {recipe.id} {recipe.version}: {commands}; contacts {', '.join(recipe.contacts())}")
    except engine.RecipeError as exc:
        failed = True
        print(f"FAIL {path.relative_to(ROOT)}: {exc}")
sys.exit(1 if failed else 0)
