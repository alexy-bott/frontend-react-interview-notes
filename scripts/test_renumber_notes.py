from __future__ import annotations

import unittest
import tempfile
from pathlib import Path

from scripts import note_paths
from scripts.renumber_notes import apply_moves, validate_moves


ROOT = Path(__file__).resolve().parents[1]


class ValidateMovesTests(unittest.TestCase):
    def test_rejects_source_escaping_notes_root_with_parent_directory(self) -> None:
        root = (Path(__file__).resolve().parents[1] / "notes").resolve()
        escaped_source = root / ".." / "outside" / "source.md"
        target = root / "01 Target.md"

        with self.assertRaises(ValueError):
            validate_moves({escaped_source: target}, root)
        with self.assertRaises(ValueError):
            apply_moves({escaped_source: target}, root)

    def test_rejects_lexically_distinct_sources_with_same_normalized_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            notes_root = Path(temporary) / "notes"
            section = notes_root / "Section"
            section.mkdir(parents=True)
            source = section / "Source.md"
            source_alias = section / ".." / "Section" / "Source.md"

            with self.assertRaisesRegex(ValueError, "sources"):
                validate_moves(
                    {
                        source: section / "01 Source.md",
                        source_alias: section / "02 Source.md",
                    },
                    notes_root,
                )


class ActiveMarkdownFilesTests(unittest.TestCase):
    def test_returns_only_root_readme_notes_and_templates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo_root = Path(temporary)
            root_readme = repo_root / "README.md"
            note = repo_root / "notes" / "Section" / "A.md"
            template = repo_root / "_templates" / "nested" / "template.md"
            history = repo_root / "docs" / "superpowers" / "history.md"
            for path in (root_readme, note, template, history):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("content\n", encoding="utf-8")

            active_markdown_files = getattr(note_paths, "active_markdown_files", None)
            self.assertIsNotNone(active_markdown_files)
            assert active_markdown_files is not None
            self.assertEqual(
                active_markdown_files(repo_root),
                sorted(path.resolve() for path in (root_readme, note, template)),
            )

    def test_apply_moves_rewrites_root_readme_and_templates_but_not_history(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo_root = Path(temporary)
            notes_root = repo_root / "notes"
            source = notes_root / "Section" / "Old.md"
            target = notes_root / "Section" / "02 New.md"
            root_readme = repo_root / "README.md"
            template = repo_root / "_templates" / "template.md"
            history = repo_root / "docs" / "superpowers" / "history.md"
            source.parent.mkdir(parents=True)
            template.parent.mkdir(parents=True)
            history.parent.mkdir(parents=True)
            source.write_text("# Old\n", encoding="utf-8")
            root_readme.write_text("[note](<./notes/Section/Old.md>)\n", encoding="utf-8")
            template.write_text("[note](<../notes/Section/Old.md>)\n", encoding="utf-8")
            history.write_text("[note](<../../notes/Section/Old.md>)\n", encoding="utf-8")

            apply_moves({source.resolve(): target.resolve()}, notes_root)

            self.assertEqual(
                root_readme.read_text(encoding="utf-8"),
                "[note](<notes/Section/02 New.md>)\n",
            )
            self.assertEqual(
                template.read_text(encoding="utf-8"),
                "[note](<../notes/Section/02 New.md>)\n",
            )
            self.assertEqual(
                history.read_text(encoding="utf-8"),
                "[note](<../../notes/Section/Old.md>)\n",
            )


if __name__ == "__main__":
    unittest.main()
