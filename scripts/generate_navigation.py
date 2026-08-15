from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from .note_paths import display_title, markdown_destination, section_order
except ImportError:
    from note_paths import display_title, markdown_destination, section_order


ROOT = Path(__file__).resolve().parents[1]
NOTES_ROOT = ROOT / "notes"

TOP_NAV_RE = re.compile(
    r"(?ms)<!-- NOTE-NAV-TOP:START -->\n.*?\n<!-- NOTE-NAV-TOP:END -->"
)
BOTTOM_NAV_RE = re.compile(
    r"(?ms)<!-- NOTE-NAV-BOTTOM:START -->\n.*?\n<!-- NOTE-NAV-BOTTOM:END -->"
)
SECTION_NAV_RE = re.compile(
    r"(?ms)<!-- SECTION-NAV:START -->\n.*?\n<!-- SECTION-NAV:END -->"
)


def replace_once(text: str, pattern: re.Pattern[str], replacement: str, path: Path) -> str:
    updated, count = pattern.subn(lambda _: replacement, text)
    if count != 1:
        raise ValueError(f"{path.relative_to(ROOT)}: expected one navigation block, found {count}")
    return updated


def note_navigation(note: Path, ordered: list[Path]) -> str:
    index = ordered.index(note.resolve())
    parts: list[str] = []

    if index > 0:
        previous = ordered[index - 1]
        parts.append(f"[← {display_title(previous)}]({markdown_destination(note, previous)})")

    parts.append(f"[↑ {note.parent.name}](<./README.md>)")
    parts.append("[⌂ Все разделы](<../../README.md>)")

    if index + 1 < len(ordered):
        following = ordered[index + 1]
        parts.append(f"[{display_title(following)} →]({markdown_destination(note, following)})")

    return " · ".join(parts)


def render_note(note: Path, ordered: list[Path]) -> str:
    text = note.read_text(encoding="utf-8")
    nav = note_navigation(note, ordered)
    top = f"<!-- NOTE-NAV-TOP:START -->\n{nav}\n<!-- NOTE-NAV-TOP:END -->"
    bottom = f"<!-- NOTE-NAV-BOTTOM:START -->\n{nav}\n<!-- NOTE-NAV-BOTTOM:END -->"
    text = replace_once(text, TOP_NAV_RE, top, note)
    return replace_once(text, BOTTOM_NAV_RE, bottom, note)


def render_section(readme: Path, ordered: list[Path]) -> str:
    text = readme.read_text(encoding="utf-8")
    first_note = ordered[0]
    block = f"""<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →]({markdown_destination(readme, first_note)})

Заметок в разделе: **{len(ordered)}**
<!-- SECTION-NAV:END -->"""
    return replace_once(text, SECTION_NAV_RE, block, readme)


def notes_label(count: int) -> str:
    remainder_100 = count % 100
    remainder_10 = count % 10
    if 11 <= remainder_100 <= 14:
        word = "заметок"
    elif remainder_10 == 1:
        word = "заметка"
    elif 2 <= remainder_10 <= 4:
        word = "заметки"
    else:
        word = "заметок"
    return f"{count} {word}"


def render_root(section_counts: dict[str, int]) -> str:
    root_readme = ROOT / "README.md"
    text = root_readme.read_text(encoding="utf-8")
    for section, count in section_counts.items():
        pattern = re.compile(
            rf"(?m)^(- \[{re.escape(section)}\]\(<\./notes/{re.escape(section)}/README\.md>\) — )"
            r"\d+ (?:заметка|заметки|заметок)\.$"
        )
        text, replacements = pattern.subn(
            lambda match: f"{match.group(1)}{notes_label(count)}.",
            text,
        )
        if replacements != 1:
            raise ValueError(f"README.md: expected one section entry for {section}, found {replacements}")
    return text


def expected_outputs() -> dict[Path, str]:
    result: dict[Path, str] = {}
    section_counts: dict[str, int] = {}

    for section_dir in sorted(path for path in NOTES_ROOT.iterdir() if path.is_dir()):
        readme = section_dir / "README.md"
        if not readme.exists():
            raise ValueError(f"{readme.relative_to(ROOT)} is missing")
        ordered = section_order(readme)
        section_counts[section_dir.name] = len(ordered)
        result[readme] = render_section(readme, ordered)
        for note in ordered:
            result[note] = render_note(note, ordered)

    result[ROOT / "README.md"] = render_root(section_counts)
    return result


def check_outputs(expected: dict[Path, str]) -> int:
    outdated = [path for path, content in expected.items() if path.read_text(encoding="utf-8") != content]
    if outdated:
        print("Navigation is not up to date:")
        for path in outdated:
            print(f"- {path.relative_to(ROOT)}")
        return 1

    print(f"Navigation is up to date: {len(expected)} Markdown files.")
    return 0


def write_outputs(expected: dict[Path, str]) -> None:
    changed = 0
    for path, content in expected.items():
        if path.read_text(encoding="utf-8") == content:
            continue
        path.write_text(content, encoding="utf-8", newline="\n")
        changed += 1
        print(f"Updated {path.relative_to(ROOT)}")
    print(f"Navigation updated: {changed} files changed.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate note navigation from section maps.")
    parser.add_argument("--check", action="store_true", help="Fail if navigation is outdated.")
    args = parser.parse_args()

    try:
        expected = expected_outputs()
    except ValueError as error:
        print(f"Navigation generation failed: {error}")
        return 1

    if args.check:
        return check_outputs(expected)
    write_outputs(expected)
    return 0


if __name__ == "__main__":
    sys.exit(main())
