from __future__ import annotations

import argparse
import sys
import uuid
from collections.abc import Mapping
from pathlib import Path

try:
    from .note_paths import display_title, numbered_filename, rewrite_internal_links, section_order
except ImportError:
    from note_paths import display_title, numbered_filename, rewrite_internal_links, section_order


ROOT = Path(__file__).resolve().parents[1]
NOTES_ROOT = ROOT / "notes"


def planned_moves(notes_root: Path) -> dict[Path, Path]:
    moves: dict[Path, Path] = {}
    for section in sorted(path for path in notes_root.iterdir() if path.is_dir()):
        ordered = section_order(section / "README.md")
        for position, source in enumerate(ordered, start=1):
            target = source.with_name(numbered_filename(position, display_title(source)))
            if source != target:
                moves[source.resolve()] = target.resolve()
    return moves


def validate_moves(moves: Mapping[Path, Path], notes_root: Path) -> None:
    root = notes_root.resolve()
    normalized_moves: dict[Path, Path] = {}

    for source, target in moves.items():
        if not source.is_absolute() or not target.is_absolute():
            raise ValueError("move paths must be absolute")
        normalized_moves[source.resolve()] = target.resolve()

    sources = set(normalized_moves)
    targets = list(normalized_moves.values())

    for source, target in normalized_moves.items():
        for path in (source, target):
            try:
                path.relative_to(root)
            except ValueError as error:
                raise ValueError(f"move path is outside notes root: {path}") from error

    if len(set(targets)) != len(targets):
        raise ValueError("move targets must be unique")

    for target in targets:
        if target.exists() and target not in sources:
            raise ValueError(f"move target already exists: {target}")


def apply_moves(moves: Mapping[Path, Path], notes_root: Path) -> None:
    root = notes_root.resolve()
    validate_moves(moves, root)
    moves = {source.resolve(): target.resolve() for source, target in moves.items()}
    markdown_files = sorted(root.rglob("*.md"))
    display_names = {source: display_title(source) for source in moves}
    rewritten: dict[Path, str] = {}

    for source in markdown_files:
        source = source.resolve()
        target = moves.get(source, source)
        text = source.read_text(encoding="utf-8")
        rewritten[target] = rewrite_internal_links(text, source, target, moves, display_names)

    temporary_moves: dict[Path, Path] = {}
    for source in moves:
        temporary = source.with_name(f".{source.name}.{uuid.uuid4().hex}.tmp")
        while temporary.exists():
            temporary = source.with_name(f".{source.name}.{uuid.uuid4().hex}.tmp")
        source.rename(temporary)
        temporary_moves[temporary] = moves[source]

    for temporary, target in temporary_moves.items():
        temporary.rename(target)

    for path, text in rewritten.items():
        if path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Renumber notes according to section navigation.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Report paths that need renumbering.")
    mode.add_argument("--write", action="store_true", help="Rename notes and rewrite internal links.")
    args = parser.parse_args()

    try:
        moves = planned_moves(NOTES_ROOT)
        validate_moves(moves, NOTES_ROOT)
    except ValueError as error:
        print(f"Renumbering failed: {error}")
        return 1

    if args.check:
        if moves:
            print(f"{len(moves)} note paths need renumbering")
            return 1
        print("All note paths are numbered.")
        return 0

    apply_moves(moves, NOTES_ROOT)
    print(f"Renumbered {len(moves)} note paths.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
