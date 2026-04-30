#!/usr/bin/env python3
"""
Build all skills under skills/ into .skill files in dist/.

Each .skill file is a zip archive of the skill folder, ready to install
in Claude. Run this script after editing any skill source folder.

Usage:
    python scripts/build_all.py            # builds everything
    python scripts/build_all.py anti-slop  # builds one skill by name

Validation: each skill is validated against Claude's skill schema before
packaging. If a SKILL.md is malformed (missing name, description too long,
etc.), packaging is aborted for that skill and an error is printed.
"""

from __future__ import annotations

import fnmatch
import sys
import zipfile
from pathlib import Path

# Patterns to exclude when packaging.
EXCLUDE_DIRS = {"__pycache__", "node_modules", ".git"}
EXCLUDE_GLOBS = {"*.pyc", "*.pyo"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}

# Skill spec limits (matches Anthropic's official validator).
MAX_NAME_LEN = 64
MAX_DESCRIPTION_LEN = 1024


def should_exclude(rel_path: Path) -> bool:
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    """Read the YAML-ish frontmatter from a SKILL.md file (no PyYAML dep)."""
    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        raise ValueError(f"{skill_md} does not start with frontmatter '---'")
    _, frontmatter, _ = content.split("---", 2)
    fields: dict[str, str] = {}
    current_key: str | None = None
    for line in frontmatter.strip().splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            current_key = key.strip()
            fields[current_key] = value.strip()
        elif current_key:
            # continuation line
            fields[current_key] += " " + line.strip()
    return fields


def validate_skill(skill_dir: Path) -> list[str]:
    """Return a list of validation errors (empty list = valid)."""
    errors: list[str] = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"Missing SKILL.md in {skill_dir}")
        return errors

    try:
        fm = parse_frontmatter(skill_md)
    except Exception as exc:
        errors.append(f"Could not parse frontmatter: {exc}")
        return errors

    name = fm.get("name", "")
    description = fm.get("description", "")

    if not name:
        errors.append("Missing 'name' in frontmatter")
    elif len(name) > MAX_NAME_LEN:
        errors.append(f"name is {len(name)} chars (max {MAX_NAME_LEN})")

    if not description:
        errors.append("Missing 'description' in frontmatter")
    elif len(description) > MAX_DESCRIPTION_LEN:
        errors.append(
            f"description is {len(description)} chars (max {MAX_DESCRIPTION_LEN})"
        )

    if name and name != skill_dir.name:
        errors.append(
            f"frontmatter name '{name}' does not match folder name '{skill_dir.name}'"
        )

    return errors


def package_skill(skill_dir: Path, dist_dir: Path) -> Path:
    """Zip a skill folder into dist/<name>.skill. Returns the output path."""
    output = dist_dir / f"{skill_dir.name}.skill"
    if output.exists():
        output.unlink()

    parent = skill_dir.parent
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(skill_dir.rglob("*")):
            rel = path.relative_to(parent)
            if should_exclude(rel):
                continue
            if path.is_file():
                zf.write(path, rel)
    return output


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    skills_dir = repo_root / "skills"
    dist_dir = repo_root / "dist"
    dist_dir.mkdir(exist_ok=True)

    if not skills_dir.is_dir():
        print(f"❌ skills/ folder not found at {skills_dir}")
        return 1

    target = sys.argv[1] if len(sys.argv) > 1 else None
    candidates = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    if target:
        candidates = [p for p in candidates if p.name == target]
        if not candidates:
            print(f"❌ no skill named '{target}' under skills/")
            return 1

    failures: list[str] = []
    for skill_dir in candidates:
        print(f"\n📦 {skill_dir.name}")
        errors = validate_skill(skill_dir)
        if errors:
            for err in errors:
                print(f"   ❌ {err}")
            failures.append(skill_dir.name)
            continue
        output = package_skill(skill_dir, dist_dir)
        size_kb = output.stat().st_size // 1024
        print(f"   ✓ built dist/{output.name} ({size_kb} KB)")

    print()
    if failures:
        print(f"❌ {len(failures)} skill(s) failed: {', '.join(failures)}")
        return 1
    print(f"✅ built {len(candidates)} skill(s) into dist/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
