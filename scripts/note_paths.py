from __future__ import annotations

import os
import re
from collections.abc import Callable, Mapping
from pathlib import Path


NUMBERED_NOTE_RE = re.compile(r"^(?P<number>\d{2}) (?P<title>.+)\.md$")
INVALID_TITLE_RE = re.compile(r'[<>:"/\\|?*]')
LINK_RE = re.compile(
    r"\[(?P<label>[^\]]*)\]\((?:<(?P<angle_destination>[^>]+)>|(?P<bare_destination>[^\s)]+))\)"
)
BACKTICK_RUN_RE = re.compile(r"`+")
SECTION_NAV_RE = re.compile(
    r"(?ms)^\s*<!-- SECTION-NAV:START -->.*?^\s*<!-- SECTION-NAV:END -->\s*(?:\n|\Z)"
)
URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
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


def active_markdown_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    root_readme = repo_root / "README.md"
    if root_readme.is_file():
        files.append(root_readme.resolve())
    for directory_name in ("notes", "_templates"):
        directory = repo_root / directory_name
        if directory.is_dir():
            files.extend(path.resolve() for path in directory.rglob("*.md") if path.is_file())
    return sorted(files)


def is_external_destination(destination: str) -> bool:
    return destination.startswith(("#", "//")) or bool(URI_SCHEME_RE.match(destination))


def link_destination(match: re.Match[str]) -> str:
    return (match.group("angle_destination") or match.group("bare_destination") or "").strip()


def _inline_code_spans(text: str) -> list[tuple[int, int]]:
    runs = list(BACKTICK_RUN_RE.finditer(text))
    spans: list[tuple[int, int]] = []
    opener_index = 0

    while opener_index < len(runs):
        opener = runs[opener_index]
        opener_length = opener.end() - opener.start()
        closer_index = next(
            (
                candidate_index
                for candidate_index in range(opener_index + 1, len(runs))
                if runs[candidate_index].end() - runs[candidate_index].start()
                == opener_length
            ),
            None,
        )
        if closer_index is None:
            opener_index += 1
            continue

        spans.append((opener.start(), runs[closer_index].end()))
        opener_index = closer_index + 1

    return spans


def _text_outside_inline_code(text: str) -> str:
    parts: list[str] = []
    position = 0
    for start, end in _inline_code_spans(text):
        parts.append(text[position:start])
        position = end
    parts.append(text[position:])
    return "".join(parts)


def text_outside_fences(text: str) -> str:
    parts: list[str] = []
    outside: list[str] = []
    in_fence = False

    def flush_outside() -> None:
        if outside:
            parts.append(_text_outside_inline_code("".join(outside)))
            outside.clear()

    for line in text.splitlines(keepends=True):
        if line.strip().startswith(("```", "~~~")):
            flush_outside()
            in_fence = not in_fence
        elif not in_fence:
            outside.append(line)
    flush_outside()
    return "".join(parts)


def section_manual_text(text: str) -> str:
    return text_outside_fences(SECTION_NAV_RE.sub("", text))


def section_order(readme: Path) -> list[Path]:
    text = section_manual_text(readme.read_text(encoding="utf-8"))
    expected = {
        path.resolve()
        for path in readme.parent.glob("*.md")
        if path.name != "README.md"
    }
    ordered: list[Path] = []

    for match in LINK_RE.finditer(text):
        target = link_destination(match)
        if not target or is_external_destination(target):
            continue
        destination = (readme.parent / target.partition("#")[0]).resolve()
        if destination in ordered:
            raise ValueError(f"{readme}: duplicate manual navigation target: {target}")
        if destination in expected:
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


def _rewrite_links_outside_inline_code(
    text: str, rewrite: Callable[[re.Match[str]], str]
) -> str:
    parts: list[str] = []
    position = 0
    for start, end in _inline_code_spans(text):
        parts.append(LINK_RE.sub(rewrite, text[position:start]))
        parts.append(text[start:end])
        position = end
    parts.append(LINK_RE.sub(rewrite, text[position:]))
    return "".join(parts)


def _rewrite_links_outside_fences(text: str, rewrite: Callable[[re.Match[str]], str]) -> str:
    parts: list[str] = []
    outside: list[str] = []
    in_fence = False

    def flush_outside() -> None:
        if outside:
            parts.append(_rewrite_links_outside_inline_code("".join(outside), rewrite))
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
) -> str:
    current_old = current_old.resolve()
    current_new = current_new.resolve()

    def rewrite(match: re.Match[str]) -> str:
        destination = link_destination(match)
        if not destination or is_external_destination(destination):
            return match.group(0)

        path_text, separator, fragment = destination.partition("#")
        old_target = (current_old.parent / path_text).resolve()
        new_target = path_moves.get(old_target, old_target)
        new_destination = os.path.relpath(new_target, current_new.parent).replace(os.sep, "/")
        if "/" not in new_destination and not new_destination.startswith("."):
            new_destination = f"./{new_destination}"
        if separator:
            new_destination = f"{new_destination}#{fragment}"

        label = match.group("label")
        needs_angle_brackets = (
            match.group("angle_destination") is not None
            or bool(re.search(r"\s", new_destination))
        )
        target = f"<{new_destination}>" if needs_angle_brackets else new_destination
        return f"[{label}]({target})"

    return _rewrite_links_outside_fences(text, rewrite)
