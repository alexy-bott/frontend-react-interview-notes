from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES_ROOT = ROOT / "notes"
LINK_RE = re.compile(r"\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))\)")
RELATED_RE = re.compile(r"(?ms)^## Связанные темы\s*\n(?P<body>.*?)(?=^## |\Z)")
DETAILS_RE = re.compile(r"(?ms)<details>.*?</details>")


def text_outside_fences(text: str) -> str:
    result: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if not in_fence:
            result.append(re.sub(r"`+[^`\n]*`+", "", line))
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


def internal_targets(file: Path, text: str) -> list[Path]:
    targets: list[Path] = []
    for match in LINK_RE.finditer(text):
        target = (match.group(1) or match.group(2) or "").strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path_text = target.partition("#")[0]
        targets.append((file.parent / path_text).resolve())
    return targets


def main() -> int:
    errors: list[str] = []
    notes = sorted(path for path in NOTES_ROOT.rglob("*.md") if path.name != "README.md")
    note_set = {note.resolve() for note in notes}
    related_inbound = {note.resolve(): 0 for note in notes}

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
        if visible.count("<details>") != visible.count("</details>"):
            errors.append(f"{relative}: unbalanced details block")

        details_blocks = DETAILS_RE.findall(visible)
        for block in details_blocks:
            if not re.fullmatch(
                r"(?s)<details>\n<summary>.+?</summary>\n\n"
                r"<dl>\n<dd>\n<h2></h2>\n\n.+?\n\n"
                r"<h2></h2>\n</dd>\n</dl>\n\n</details>",
                block,
            ):
                errors.append(f"{relative}: details spacing is inconsistent")

        related_match = RELATED_RE.search(visible)
        if not related_match:
            errors.append(f"{relative}: related topics section is missing")
        else:
            related_targets = internal_targets(note, related_match.group("body"))
            if len(related_targets) < 2:
                errors.append(f"{relative}: expected at least two related topics")
            if len(set(related_targets)) != len(related_targets):
                errors.append(f"{relative}: duplicate related topic")
            if note.resolve() in related_targets:
                errors.append(f"{relative}: related topics contain a self-link")
            for target in related_targets:
                if target in note_set and target != note.resolve():
                    related_inbound[target] += 1
        check_links(note, text, errors)

    for note in notes:
        if related_inbound[note.resolve()] == 0:
            errors.append(f"{note.relative_to(ROOT)}: no incoming related-topic link")

    section_readmes = sorted(NOTES_ROOT.rglob("README.md"))
    for readme in section_readmes:
        text = readme.read_text(encoding="utf-8")
        section_notes = sorted(path for path in readme.parent.glob("*.md") if path.name != "README.md")
        relative = readme.relative_to(ROOT)
        if text.count("SECTION-NAV:START") != 1 or text.count("SECTION-NAV:END") != 1:
            errors.append(f"{relative}: section navigation is missing or duplicated")
        if f"Заметок в разделе: **{len(section_notes)}**" not in text:
            errors.append(f"{relative}: note count is incorrect")
        if text.count("Начать с первой заметки →") != 1:
            errors.append(f"{relative}: start link is missing or duplicated")
        if len(re.findall(r"^# [^#]", text_outside_fences(text), flags=re.MULTILINE)) != 1:
            errors.append(f"{relative}: expected exactly one H1")
        if not re.search(r"^## [^#]", text_outside_fences(text), flags=re.MULTILINE):
            errors.append(f"{relative}: expected at least one H2")
        if "[[" in text_outside_fences(text):
            errors.append(f"{relative}: unresolved Obsidian wikilink")
        readme_targets = set(internal_targets(readme, text))
        for note in section_notes:
            if note.resolve() not in readme_targets:
                errors.append(f"{relative}: {note.name} is missing from navigation")

    root_readme = ROOT / "README.md"
    root_targets = set(internal_targets(root_readme, root_readme.read_text(encoding="utf-8")))
    for readme in section_readmes:
        if readme.resolve() not in root_targets:
            errors.append(f"README.md: {readme.parent.name} section is missing from navigation")

    for readme in [root_readme, *section_readmes]:
        check_links(readme, readme.read_text(encoding="utf-8"), errors)

    if errors:
        print("Notes check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    sections = len({note.parent for note in notes})
    print(f"Notes check passed: {len(notes)} notes in {sections} sections.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
