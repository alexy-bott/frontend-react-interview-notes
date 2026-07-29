from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "Конспект для подготовки"
WIKILINK_RE = re.compile(r"!?\[\[([^\]]+)\]\]")
RELATED_RE = re.compile(r"(?ms)^#### Связанные темы\s*\n(?P<body>.*?)(?=^#### |\Z)")
SOURCES_RE = re.compile(r"(?ms)^#### Источники\s*\n(?P<body>.*?)(?=^#### |\Z)")


def without_code(text: str) -> str:
    result: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith(("```", "~~~")):
            in_fence = not in_fence
            result.append("")
            continue
        if in_fence:
            result.append("")
            continue
        line = re.sub(r"`+[^`\n]*`+", "", line)
        line = re.sub(r"<code>.*?</code>", "", line)
        result.append(line)
    return "\n".join(result)


def has_valid_frontmatter(text: str) -> bool:
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        return True
    return any(line.strip() == "---" for line in lines[1:])


def target_path(raw_target: str) -> str:
    target = raw_target.split("|", 1)[0].strip()
    return target.partition("#")[0].strip().replace("\\", "/")


def build_stem_index(files: list[Path]) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = defaultdict(list)
    for file in files:
        index[file.stem.casefold()].append(file.resolve())
    return index


def resolve_wikilink(current_file: Path, raw_target: str, stem_index: dict[str, list[Path]]) -> list[Path]:
    normalized = target_path(raw_target)
    if not normalized:
        return [current_file.resolve()]

    prefix = f"{SOURCE_ROOT.name}/"
    if normalized.startswith(prefix):
        normalized = normalized[len(prefix) :]
    normalized = normalized.removesuffix(".md")

    candidates = [
        SOURCE_ROOT / f"{normalized}.md",
        current_file.parent / f"{normalized}.md",
    ]
    exact = []
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.exists() and resolved not in exact:
            exact.append(resolved)
    if exact:
        return exact

    return stem_index.get(Path(normalized).name.casefold(), [])


def wikilinks(text: str) -> list[tuple[str, int]]:
    visible = without_code(text)
    return [
        (match.group(1), visible.count("\n", 0, match.start()) + 1)
        for match in WIKILINK_RE.finditer(visible)
    ]


def main() -> int:
    errors: list[str] = []
    files = sorted(SOURCE_ROOT.rglob("*.md"))
    directories = sorted(path for path in SOURCE_ROOT.iterdir() if path.is_dir())
    content_notes = sorted(file for file in files if file.parent != SOURCE_ROOT)
    maps = sorted(file for file in files if file.parent == SOURCE_ROOT and file.name != "00 Карта подготовки.md")
    stem_index = build_stem_index(files)
    resolved_links = 0
    related_inbound = {note.resolve(): 0 for note in content_notes}

    if len(files) != 286:
        errors.append(f"expected 286 Markdown files, found {len(files)}")
    if len(directories) != 23:
        errors.append(f"expected 23 section directories, found {len(directories)}")
    if len(content_notes) != 262:
        errors.append(f"expected 262 content notes, found {len(content_notes)}")

    casefold_paths: dict[str, Path] = {}
    for file in files:
        relative = file.relative_to(ROOT)
        folded = relative.as_posix().casefold()
        if folded in casefold_paths:
            errors.append(f"case-insensitive path collision: {casefold_paths[folded]} and {relative}")
        casefold_paths[folded] = relative

        try:
            text = file.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError as error:
            errors.append(f"{relative}: invalid UTF-8 ({error})")
            continue

        if not text.strip():
            errors.append(f"{relative}: empty file")
            continue
        if not has_valid_frontmatter(text):
            errors.append(f"{relative}: unclosed frontmatter")

        visible = without_code(text)
        if re.search(r"(?m)^(<<<<<<<|=======|>>>>>>>)", visible):
            errors.append(f"{relative}: merge conflict marker outside a code block")

        for raw_target, line in wikilinks(text):
            targets = resolve_wikilink(file, raw_target, stem_index)
            if not targets:
                errors.append(f"{relative}:{line}: unresolved wikilink [[{raw_target}]]")
            elif len(targets) > 1:
                choices = ", ".join(str(path.relative_to(ROOT)) for path in targets[:4])
                errors.append(f"{relative}:{line}: ambiguous wikilink [[{raw_target}]] -> {choices}")
            else:
                resolved_links += 1

    for note in content_notes:
        relative = note.relative_to(ROOT)
        text = note.read_text(encoding="utf-8-sig")
        visible = without_code(text)

        quick_count = len(re.findall(r"(?m)^#### (?:Быстрый ответ|Ответ на 60 секунд)\s*$", visible))
        if quick_count != 1:
            errors.append(f"{relative}: expected one quick-answer heading, found {quick_count}")

        related_matches = list(RELATED_RE.finditer(visible))
        if len(related_matches) != 1:
            errors.append(f"{relative}: expected one related-topics section, found {len(related_matches)}")
        else:
            related_targets: list[Path] = []
            for raw_target, _ in wikilinks(related_matches[0].group("body")):
                targets = resolve_wikilink(note, raw_target, stem_index)
                if len(targets) == 1:
                    related_targets.append(targets[0])

            if len(related_targets) < 2:
                errors.append(f"{relative}: expected at least two related topics")
            if len(set(related_targets)) != len(related_targets):
                errors.append(f"{relative}: duplicate related topic")
            if note.resolve() in related_targets:
                errors.append(f"{relative}: related topics contain a self-link")
            for target in related_targets:
                if target in related_inbound and target != note.resolve():
                    related_inbound[target] += 1

        source_matches = list(SOURCES_RE.finditer(visible))
        if len(source_matches) != 1:
            errors.append(f"{relative}: expected one sources section, found {len(source_matches)}")
        elif not re.search(r"https?://", source_matches[0].group("body")):
            errors.append(f"{relative}: sources section has no external link")

    for note, inbound in related_inbound.items():
        if inbound == 0:
            errors.append(f"{note.relative_to(ROOT)}: no incoming related-topic link")

    for directory in directories:
        section_map = SOURCE_ROOT / f"{directory.name}.md"
        if not section_map.exists():
            errors.append(f"{section_map.relative_to(ROOT)}: section map is missing")
            continue
        map_targets: set[Path] = set()
        for raw_target, _ in wikilinks(section_map.read_text(encoding="utf-8-sig")):
            targets = resolve_wikilink(section_map, raw_target, stem_index)
            if len(targets) == 1:
                map_targets.add(targets[0])
        for note in directory.glob("*.md"):
            if note.resolve() not in map_targets:
                errors.append(f"{section_map.relative_to(ROOT)}: {note.name} is missing from the section map")

    root_map = SOURCE_ROOT / "00 Карта подготовки.md"
    root_targets: set[Path] = set()
    for raw_target, _ in wikilinks(root_map.read_text(encoding="utf-8-sig")):
        targets = resolve_wikilink(root_map, raw_target, stem_index)
        if len(targets) == 1:
            root_targets.add(targets[0])
    for section_map in maps:
        if section_map.resolve() not in root_targets:
            errors.append(f"{root_map.relative_to(ROOT)}: {section_map.name} is missing from the root map")

    if errors:
        print("Source audit failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Source audit passed: "
        f"{len(files)} files, {len(directories)} sections, "
        f"{len(content_notes)} notes, {resolved_links} resolved wikilinks."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
