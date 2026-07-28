from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES_ROOT = ROOT / "notes"
LINK_RE = re.compile(r"\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))\)")


def text_outside_fences(text: str) -> str:
    result: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if not in_fence:
            result.append(line)
    return "\n".join(result)


def check_links(file: Path, text: str, errors: list[str]) -> None:
    for match in LINK_RE.finditer(text_outside_fences(text)):
        target = (match.group(1) or match.group(2) or "").strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path_text = target.partition("#")[0]
        destination = (file.parent / path_text).resolve()
        if not destination.exists():
            errors.append(f"{file.relative_to(ROOT)}: broken link -> {target}")


def main() -> int:
    errors: list[str] = []
    notes = sorted(path for path in NOTES_ROOT.rglob("*.md") if path.name != "README.md")

    if not (ROOT / "README.md").exists():
        errors.append("README.md is missing")
    if not notes:
        errors.append("No notes found")

    for note in notes:
        text = note.read_text(encoding="utf-8")
        visible = text_outside_fences(text)
        relative = note.relative_to(ROOT)

        if not (note.parent / "README.md").exists():
            errors.append(f"{relative}: section README.md is missing")
        if len(re.findall(r"^# [^#]", visible, flags=re.MULTILINE)) != 1:
            errors.append(f"{relative}: expected exactly one H1")
        if visible.lstrip().startswith("---") or "\naliases:\n" in visible:
            errors.append(f"{relative}: Obsidian frontmatter was not removed")
        for marker in ("NOTE-NAV-TOP:START", "NOTE-NAV-TOP:END", "NOTE-NAV-BOTTOM:START", "NOTE-NAV-BOTTOM:END"):
            if text.count(marker) != 1:
                errors.append(f"{relative}: expected one {marker}")
        for heading in ("## Быстрый ответ", "## Связанные темы", "## Источники"):
            if visible.count(heading) != 1:
                errors.append(f"{relative}: expected one '{heading}'")
        if re.search(r"^#{4,6} ", visible, flags=re.MULTILINE):
            errors.append(f"{relative}: headings deeper than H3 are not allowed")
        if "[[" in visible:
            errors.append(f"{relative}: unresolved Obsidian wikilink")
        if re.search(r"^>\s*\[!", visible, flags=re.MULTILINE):
            errors.append(f"{relative}: unresolved Obsidian callout")
        if text.count("<details>") != text.count("</details>"):
            errors.append(f"{relative}: unbalanced details block")

        check_links(note, text, errors)

    for readme in [ROOT / "README.md", *NOTES_ROOT.rglob("README.md")]:
        check_links(readme, readme.read_text(encoding="utf-8"), errors)

    if errors:
        print("Notes check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    sections = len({note.parent for note in notes})
    print(f"Notes check passed: {len(notes)} pilot notes in {sections} sections.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
