from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from scripts.note_paths import (
        LINK_RE,
        display_title,
        is_external_destination,
        link_destination,
        parse_numbered_name,
        section_manual_text,
        section_order,
        text_outside_fences,
    )
except ModuleNotFoundError:
    from note_paths import (
        LINK_RE,
        display_title,
        is_external_destination,
        link_destination,
        parse_numbered_name,
        section_manual_text,
        section_order,
        text_outside_fences,
    )


ROOT = Path(__file__).resolve().parents[1]
NOTES_ROOT = ROOT / "notes"
RELATED_RE = re.compile(r"(?ms)^## Связанные темы\s*\n(?P<body>.*?)(?=^## |\Z)")
DETAILS_RE = re.compile(r"(?ms)<details>.*?</details>")


def note_identity_errors(note: Path, visible: str) -> list[str]:
    errors: list[str] = []
    try:
        _, expected_title = parse_numbered_name(note)
    except ValueError:
        return [f"invalid numeric prefix: {note.name}"]
    headings = re.findall(r"^# ([^#].*)$", visible, flags=re.MULTILINE)
    if len(headings) == 1 and headings[0] != expected_title:
        errors.append(f"H1 differs from filename: expected {expected_title}")
    return errors


def section_numbering_errors(readme: Path, ordered: list[Path]) -> list[str]:
    numbers = [parse_numbered_name(path)[0] for path in ordered]
    expected = list(range(1, len(ordered) + 1))
    errors: list[str] = []
    if numbers != expected:
        errors.append(f"README order differs from numeric order: {numbers}")
    if sorted(numbers) != expected:
        errors.append(f"non-contiguous numbering: {sorted(numbers)}")
    return errors


def check_links(file: Path, text: str, errors: list[str]) -> None:
    for match in LINK_RE.finditer(text_outside_fences(text)):
        target = link_destination(match)
        if not target or is_external_destination(target):
            continue
        path_text = target.partition("#")[0]
        destination = (file.parent / path_text).resolve()
        if not destination.exists():
            errors.append(f"{file.relative_to(ROOT)}: broken link -> {target}")


def internal_targets(file: Path, text: str) -> list[Path]:
    targets: list[Path] = []
    for match in LINK_RE.finditer(text_outside_fences(text)):
        target = link_destination(match)
        if not target or is_external_destination(target):
            continue
        path_text = target.partition("#")[0]
        targets.append((file.parent / path_text).resolve())
    return targets


def related_topic_links(
    note: Path, text: str, note_set: set[Path]
) -> tuple[list[Path], list[str]]:
    targets: list[Path] = []
    errors: list[str] = []
    for match in LINK_RE.finditer(text_outside_fences(text)):
        destination = link_destination(match)
        if not destination or is_external_destination(destination):
            errors.append(f"related topic target is not a note: {destination}")
            continue
        path_text = destination.partition("#")[0]
        target = (note.parent / path_text).resolve()
        if target not in note_set:
            errors.append(f"related topic target is not a note: {destination}")
            continue
        targets.append(target)
    return targets, errors


def section_readme_identity_errors(
    readme: Path, text: str, section_notes: list[Path]
) -> list[str]:
    visible = section_manual_text(text)
    errors: list[str] = []
    headings = re.findall(r"^# ([^#].*)$", visible, flags=re.MULTILINE)
    if len(headings) != 1:
        errors.append("expected exactly one H1")
    elif headings[0] != readme.parent.name:
        errors.append(f"H1 differs from section directory: expected {readme.parent.name}")

    note_set = {note.resolve() for note in section_notes}
    for match in LINK_RE.finditer(visible):
        destination = link_destination(match)
        if not destination or is_external_destination(destination):
            continue
        target = (readme.parent / destination.partition("#")[0]).resolve()
        if target not in note_set:
            continue
        label = match.group("label")
        if re.match(r"^\d{2}(?:\s|$)", label):
            errors.append(f"manual note link label contains numeric prefix: {label}")
        expected_label = display_title(target)
        if label != expected_label:
            errors.append(
                "manual note link label differs from note title: "
                f"expected {expected_label}, got {label}"
            )
    return errors


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

        for error in note_identity_errors(note, visible):
            errors.append(f"{relative}: {error}")
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
            related_targets, related_errors = related_topic_links(
                note, related_match.group("body"), note_set
            )
            for error in related_errors:
                errors.append(f"{relative}: {error}")
            if len(related_targets) < 2:
                errors.append(f"{relative}: expected at least two related topics")
            if len(set(related_targets)) != len(related_targets):
                errors.append(f"{relative}: duplicate related topic")
            if note.resolve() in related_targets:
                errors.append(f"{relative}: related topics contain a self-link")
            for target in related_targets:
                if target != note.resolve():
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
        for error in section_readme_identity_errors(readme, text, section_notes):
            errors.append(f"{relative}: {error}")
        manual_visible = section_manual_text(text)
        if not re.search(r"^## [^#]", manual_visible, flags=re.MULTILINE):
            errors.append(f"{relative}: expected at least one H2")
        if "[[" in manual_visible:
            errors.append(f"{relative}: unresolved Obsidian wikilink")
        readme_targets = set(internal_targets(readme, text))
        for note in section_notes:
            if note.resolve() not in readme_targets:
                errors.append(f"{relative}: {note.name} is missing from navigation")
        try:
            ordered = section_order(readme)
        except ValueError as error:
            errors.append(str(error))
        else:
            if all(re.fullmatch(r"\d{2} .+\.md", path.name) for path in ordered):
                for error in section_numbering_errors(readme, ordered):
                    errors.append(f"{relative}: {error}")

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
