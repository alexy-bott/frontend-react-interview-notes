from __future__ import annotations

import os
import re
from collections.abc import Callable, Mapping
from pathlib import Path


NUMBERED_NOTE_RE = re.compile(r"^(?P<number>\d{2}) (?P<title>.+)\.md$")
INVALID_TITLE_RE = re.compile(r'[<>:"/\\|?*]')
LINK_RE = re.compile(r"\[[^\]]+\]\((?:<([^>]+)>|([^\s)]+))\)")
ROOT = Path(__file__).resolve().parents[1]


def parse_numbered_name(path: Path) -> tuple[int, str]:
    match = NUMBERED_NOTE_RE.fullmatch(path.name)
    if not match:
        raise ValueError(f"expected '<NN> <title>.md': {path.name}")
    return int(match.group("number")), match.group("title")


def display_title(path: Path) -> str:
    match = NUMBERED_NOTE_RE.fullmatch(path.name)
    return match.group("title") if match else path.stem


def numbered_filename(position: int, title: str) -> str:
    if not 1 <= position <= 99:
        raise ValueError(f"position must be between 1 and 99: {position}")
    if not title or INVALID_TITLE_RE.search(title):
        raise ValueError(f"invalid note title: {title!r}")
    return f"{position:02d} {title}.md"


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


def section_order(readme: Path) -> list[Path]:
    text = text_outside_fences(readme.read_text(encoding="utf-8"))
    expected = {
        path.resolve()
        for path in readme.parent.glob("*.md")
        if path.name != "README.md"
    }
    ordered: list[Path] = []

    for match in LINK_RE.finditer(text):
        target = (match.group(1) or match.group(2) or "").strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        destination = (readme.parent / target.partition("#")[0]).resolve()
        if destination in expected and destination not in ordered:
            ordered.append(destination)

    if set(ordered) != expected:
        missing = sorted(path.name for path in expected - set(ordered))
        extra = sorted(path.name for path in set(ordered) - expected)
        raise ValueError(
            f"{readme.relative_to(ROOT)}: navigation does not match section notes; "
            f"missing={missing}, extra={extra}"
        )
    if not ordered:
        raise ValueError(f"{readme.relative_to(ROOT)}: section has no notes")
    return ordered


def markdown_destination(current_file: Path, destination: Path) -> str:
    relative = os.path.relpath(destination, current_file.parent).replace(os.sep, "/")
    if "/" not in relative and not relative.startswith("."):
        relative = f"./{relative}"
    return f"<{relative}>"


def _is_external_destination(destination: str) -> bool:
    return destination.startswith(("http://", "https://", "mailto:", "#", "//")) or bool(
        re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", destination)
    )


def _rewrite_links_outside_fences(text: str, rewrite: Callable[[re.Match[str]], str]) -> str:
    parts: list[str] = []
    outside: list[str] = []
    in_fence = False

    def flush_outside() -> None:
        if outside:
            parts.append(LINK_RE.sub(rewrite, "".join(outside)))
            outside.clear()

    for line in text.splitlines(keepends=True):
        if line.strip().startswith(("```", "~~~")):
            flush_outside()
            parts.append(line)
            in_fence = not in_fence
        elif in_fence:
            parts.append(line)
        else:
            outside.append(line)
    flush_outside()
    return "".join(parts)


def rewrite_internal_links(
    text: str,
    current_old: Path,
    current_new: Path,
    path_moves: Mapping[Path, Path],
    display_names: Mapping[Path, str],
) -> str:
    current_old = current_old.resolve()
    current_new = current_new.resolve()

    def rewrite(match: re.Match[str]) -> str:
        destination = (match.group(1) or match.group(2) or "").strip()
        if not destination or _is_external_destination(destination):
            return match.group(0)

        path_text, separator, fragment = destination.partition("#")
        old_target = (current_old.parent / path_text).resolve()
        new_target = path_moves.get(old_target, old_target)
        new_destination = os.path.relpath(new_target, current_new.parent).replace(os.sep, "/")
        if "/" not in new_destination and not new_destination.startswith("."):
            new_destination = f"./{new_destination}"
        if separator:
            new_destination = f"{new_destination}#{fragment}"

        source = match.group(0)
        label = source[1 : source.rfind("](")]
        if old_target in display_names:
            label = display_names[old_target]
        target = f"<{new_destination}>" if match.group(1) is not None else new_destination
        return f"[{label}]({target})"

    return _rewrite_links_outside_fences(text, rewrite)
