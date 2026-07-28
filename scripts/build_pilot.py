from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "Конспект для подготовки"

PILOTS = {
    SOURCE_ROOT / "CSS" / "Flexbox.md": ROOT / "notes" / "CSS" / "Flexbox.md",
    SOURCE_ROOT / "JavaScript" / "Event Loop.md": ROOT / "notes" / "JavaScript" / "Event Loop.md",
}

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


def source_for_wikilink(target: str, current_source: Path) -> tuple[Path, str]:
    path_part, separator, anchor = target.partition("#")
    if not path_part:
        return current_source, f"#{anchor}" if separator else ""

    normalized = path_part.replace("\\", "/").removesuffix(".md")
    prefix = f"{SOURCE_ROOT.name}/"
    if normalized.startswith(prefix):
        normalized = normalized[len(prefix) :]

    candidate = SOURCE_ROOT / f"{normalized}.md"
    if not candidate.exists():
        candidate = current_source.parent / f"{normalized}.md"

    suffix = f"#{anchor}" if separator else ""
    return candidate, suffix


def markdown_link(match: re.Match[str], current_source: Path, output_file: Path) -> str:
    target = match.group(1).strip()
    label = (match.group(2) or "").strip()
    source_target, anchor = source_for_wikilink(target, current_source)
    destination = PILOTS.get(source_target, source_target)

    if not label:
        label = target.partition("#")[2] or Path(target.partition("#")[0]).name

    relative = os.path.relpath(destination, output_file.parent).replace(os.sep, "/")
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
                    *details,
                    "",
                    "</details>",
                ]
            )
            continue

        if not in_fence:
            if line == "#### Ответ на 60 секунд":
                line = "## Быстрый ответ"
            elif line.startswith("#### "):
                line = "## " + line[5:]
            elif line.startswith("##### "):
                line = "### " + line[6:]
            line = convert_inline_wikilinks(line, current_source, output_file)

        output.append(line)
        index += 1

    return "\n".join(output).strip()


def build_note(source: Path, output_file: Path) -> None:
    section = output_file.parent.name
    title = output_file.stem
    body = convert_body(source.read_text(encoding="utf-8"), source, output_file)
    nav = f"[↑ {section}](<./README.md>) · [⌂ Все разделы](<../../README.md>)"
    result = f"""# {title}

<!-- NOTE-NAV-TOP:START -->
{nav}
<!-- NOTE-NAV-TOP:END -->

{body}

---

<!-- NOTE-NAV-BOTTOM:START -->
{nav}
<!-- NOTE-NAV-BOTTOM:END -->
"""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(result, encoding="utf-8", newline="\n")


def main() -> None:
    for source, output_file in PILOTS.items():
        build_note(source, output_file)
        print(f"Built {output_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
