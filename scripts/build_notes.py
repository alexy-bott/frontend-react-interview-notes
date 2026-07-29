from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "Конспект для подготовки"
NOTES_ROOT = ROOT / "notes"
ROOT_MAP = SOURCE_ROOT / "00 Карта подготовки.md"

# Разделы добавляются сюда после проверки очередного тематического пакета.
MIGRATED_SECTIONS = ("HTML", "Accessibility", "CSS", "JavaScript")

SECTION_GROUPS = (
    (
        "🌐 Основы веб-платформы",
        ("HTML", "Accessibility", "CSS", "JavaScript", "Algorithms", "Browser Internals", "Web Basics"),
    ),
    (
        "🧩 Приложения и фреймворки",
        ("TypeScript", "React", "Next.js", "Forms", "Vue", "Performance", "Security"),
    ),
    (
        "🛠️ Инженерная практика",
        (
            "Architecture",
            "Frontend System Design",
            "Principles",
            "Patterns",
            "Testing",
            "DevOps",
            "Git",
            "Tooling",
            "Workflow",
        ),
    ),
)

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


def strip_frontmatter(text: str) -> str:
    text = text.lstrip("\ufeff")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :]).lstrip("\n")
    return text


def source_files() -> list[Path]:
    return sorted(SOURCE_ROOT.rglob("*.md"))


def content_sources(section: str) -> set[Path]:
    return {path.resolve() for path in (SOURCE_ROOT / section).glob("*.md")}


def source_for_wikilink(target: str, current_source: Path) -> tuple[Path, str]:
    path_part, separator, anchor = target.partition("#")
    if not path_part:
        return current_source.resolve(), f"#{anchor}" if separator else ""

    normalized = path_part.replace("\\", "/").removesuffix(".md")
    prefix = f"{SOURCE_ROOT.name}/"
    if normalized.startswith(prefix):
        normalized = normalized[len(prefix) :]

    candidates = (
        SOURCE_ROOT / f"{normalized}.md",
        current_source.parent / f"{normalized}.md",
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve(), f"#{anchor}" if separator else ""

    by_stem = [path for path in source_files() if path.stem.casefold() == Path(normalized).name.casefold()]
    if len(by_stem) == 1:
        return by_stem[0].resolve(), f"#{anchor}" if separator else ""
    raise ValueError(f"Cannot resolve wikilink [[{target}]] in {current_source.relative_to(ROOT)}")


def section_order(section: str) -> list[Path]:
    section_map = SOURCE_ROOT / f"{section}.md"
    expected = content_sources(section)
    ordered: list[Path] = []

    for match in WIKILINK_RE.finditer(section_map.read_text(encoding="utf-8-sig")):
        source, _ = source_for_wikilink(match.group(1).strip(), section_map)
        if source in expected and source not in ordered:
            ordered.append(source)

    if set(ordered) != expected:
        missing = sorted(path.name for path in expected - set(ordered))
        raise ValueError(f"{section_map.relative_to(ROOT)} does not order all notes: {missing}")
    return ordered


def output_for_source(source: Path) -> Path:
    source = source.resolve()
    if source == ROOT_MAP.resolve():
        return ROOT / "README.md"

    if source.parent == SOURCE_ROOT.resolve():
        section = source.stem
        if section in MIGRATED_SECTIONS:
            return NOTES_ROOT / section / "README.md"
        return source

    section = source.parent.name
    if section in MIGRATED_SECTIONS:
        return NOTES_ROOT / section / source.name
    return source


def markdown_destination(current_file: Path, destination: Path) -> str:
    relative = os.path.relpath(destination, current_file.parent).replace(os.sep, "/")
    if "/" not in relative and not relative.startswith("."):
        relative = f"./{relative}"
    return f"<{relative}>"


def markdown_link(match: re.Match[str], current_source: Path, output_file: Path) -> str:
    target = match.group(1).strip()
    label = (match.group(2) or "").strip()
    source_target, anchor = source_for_wikilink(target, current_source)
    destination = output_for_source(source_target)

    if not label:
        label = target.partition("#")[2] or Path(target.partition("#")[0]).name

    relative = os.path.relpath(destination, output_file.parent).replace(os.sep, "/")
    if "/" not in relative and not relative.startswith("."):
        relative = f"./{relative}"
    return f"[{label}](<{relative}{anchor}>)"


def convert_inline_wikilinks(line: str, current_source: Path, output_file: Path) -> str:
    parts = re.split(r"(`+[^`]*`+)", line)
    for index in range(0, len(parts), 2):
        parts[index] = WIKILINK_RE.sub(
            lambda match: markdown_link(match, current_source, output_file),
            parts[index],
        )
    return "".join(parts)


def convert_body(text: str, current_source: Path, output_file: Path) -> str:
    source_lines = strip_frontmatter(text).splitlines()
    output: list[str] = []
    in_fence = False
    index = 0

    while index < len(source_lines):
        line = source_lines[index]
        stripped = line.strip()

        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            output.append(line)
            index += 1
            continue

        if not in_fence and re.match(r"^>\s*\[!faq\][+-]?\s*", line):
            summary = re.sub(r"^>\s*\[!faq\][+-]?\s*", "", line).strip() or "Уточнения"
            details: list[str] = []
            index += 1
            while index < len(source_lines) and source_lines[index].startswith(">"):
                details.append(re.sub(r"^> ?", "", source_lines[index]))
                index += 1

            output.extend(
                [
                    "<details>",
                    f"<summary><strong>{summary}</strong></summary>",
                    "",
                    "<dl>",
                    "<dd>",
                    "<h2></h2>",
                    "",
                    *details,
                    "",
                    "<h2></h2>",
                    "</dd>",
                    "</dl>",
                    "",
                    "</details>",
                ]
            )
            continue

        if not in_fence:
            if line in ("#### Быстрый ответ", "#### Ответ на 60 секунд"):
                line = "## Быстрый ответ"
            elif line.startswith("#### "):
                line = "## " + line[5:]
            elif line.startswith("##### "):
                line = "### " + line[6:]
            line = convert_inline_wikilinks(line, current_source, output_file)

        output.append(line)
        index += 1

    return "\n".join(output).strip()


def note_navigation(output_file: Path, ordered_outputs: list[Path]) -> str:
    index = ordered_outputs.index(output_file)
    parts: list[str] = []

    if index > 0:
        previous = ordered_outputs[index - 1]
        parts.append(f"[← {previous.stem}]({markdown_destination(output_file, previous)})")

    parts.append(f"[↑ {output_file.parent.name}](<./README.md>)")
    parts.append("[⌂ Все разделы](<../../README.md>)")

    if index + 1 < len(ordered_outputs):
        following = ordered_outputs[index + 1]
        parts.append(f"[{following.stem} →]({markdown_destination(output_file, following)})")

    return " · ".join(parts)


def render_note(source: Path, ordered_sources: list[Path]) -> tuple[Path, str]:
    output_file = output_for_source(source)
    ordered_outputs = [output_for_source(item) for item in ordered_sources]
    body = convert_body(source.read_text(encoding="utf-8-sig"), source, output_file)
    nav = note_navigation(output_file, ordered_outputs)
    result = f"""# {source.stem}

<!-- NOTE-NAV-TOP:START -->
{nav}
<!-- NOTE-NAV-TOP:END -->

{body}

---

<!-- NOTE-NAV-BOTTOM:START -->
{nav}
<!-- NOTE-NAV-BOTTOM:END -->
"""
    return output_file, result


def render_section(section: str, ordered_sources: list[Path]) -> tuple[Path, str]:
    section_map = SOURCE_ROOT / f"{section}.md"
    output_file = NOTES_ROOT / section / "README.md"
    first_note = output_for_source(ordered_sources[0])
    body = convert_body(section_map.read_text(encoding="utf-8-sig"), section_map, output_file)
    result = f"""# {section}

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой заметки →]({markdown_destination(output_file, first_note)})

Заметок в разделе: **{len(ordered_sources)}**
<!-- SECTION-NAV:END -->

{body}
"""
    return output_file, result


def render_root(section_orders: dict[str, list[Path]]) -> tuple[Path, str]:
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

    group_blocks: list[str] = []
    for title, sections in SECTION_GROUPS:
        available = [section for section in sections if section in section_orders]
        if not available:
            continue
        links = "\n".join(
            f"- [{section}](<./notes/{section}/README.md>) — {notes_label(len(section_orders[section]))}."
            for section in available
        )
        group_blocks.append(f"### {title}\n\n{links}")

    listed = {section for _, sections in SECTION_GROUPS for section in sections}
    unknown = set(section_orders) - listed
    if unknown:
        raise ValueError(f"Sections are missing from SECTION_GROUPS: {sorted(unknown)}")

    result = f"""# Конспект для frontend-собеседований

Материалы для последовательного повторения frontend и React перед собеседованием.

## Разделы

{"\n\n".join(group_blocks)}
"""
    return ROOT / "README.md", result


def expected_outputs() -> dict[Path, str]:
    result: dict[Path, str] = {}
    section_orders = {section: section_order(section) for section in MIGRATED_SECTIONS}

    root_path, root_text = render_root(section_orders)
    result[root_path] = root_text

    for section, ordered_sources in section_orders.items():
        section_path, section_text = render_section(section, ordered_sources)
        result[section_path] = section_text
        for source in ordered_sources:
            note_path, note_text = render_note(source, ordered_sources)
            result[note_path] = note_text

    return result


def check_outputs(expected: dict[Path, str]) -> int:
    errors: list[str] = []
    for path, content in expected.items():
        if not path.exists():
            errors.append(f"missing: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != content:
            errors.append(f"outdated: {path.relative_to(ROOT)}")

    expected_notes = {path.resolve() for path in expected if NOTES_ROOT in path.parents}
    actual_notes = {path.resolve() for path in NOTES_ROOT.rglob("*.md")}
    for stale in sorted(actual_notes - expected_notes):
        errors.append(f"stale: {stale.relative_to(ROOT)}")

    if errors:
        print("Generated notes are not up to date:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Generated notes are up to date: {len(expected) - 1} files plus README.md.")
    return 0


def write_outputs(expected: dict[Path, str]) -> None:
    for path, content in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"Built {path.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build GitHub-friendly notes from the Obsidian source.")
    parser.add_argument("--check", action="store_true", help="Fail if generated files are outdated.")
    args = parser.parse_args()

    expected = expected_outputs()
    if args.check:
        return check_outputs(expected)
    write_outputs(expected)
    return 0


if __name__ == "__main__":
    sys.exit(main())
