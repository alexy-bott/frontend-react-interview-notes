from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import check_notes


ROOT = Path(__file__).resolve().parents[1]


class LinkChecksTests(unittest.TestCase):
    def test_uri_and_protocol_relative_links_are_not_treated_as_files(self) -> None:
        current = ROOT / "notes" / "Section" / "A.md"
        text = "[phone](tel:+79990000000) [asset](//cdn.example/app.js)"
        errors: list[str] = []

        check_notes.check_links(current, text, errors)

        self.assertEqual(errors, [])
        self.assertEqual(check_notes.internal_targets(current, text), [])

    def test_empty_label_link_is_still_checked(self) -> None:
        current = ROOT / "notes" / "Section" / "A.md"
        errors: list[str] = []

        check_notes.check_links(current, "[](<./missing.md>)", errors)

        self.assertEqual(len(errors), 1)
        self.assertIn("broken link", errors[0])


class SectionReadmeIdentityTests(unittest.TestCase):
    def _errors_for(self, h1: str, label: str) -> list[str]:
        with tempfile.TemporaryDirectory() as temporary:
            section = Path(temporary) / "Section"
            section.mkdir()
            note = section / "37 Promise.md"
            note.write_text("# Promise\n", encoding="utf-8")
            readme = section / "README.md"
            text = f"""# {h1}

<!-- SECTION-NAV:START -->
[01 Promise](<./37 Promise.md>)
<!-- SECTION-NAV:END -->

## Topics

- [{label}](<./37 Promise.md>)
"""
            identity_errors = getattr(check_notes, "section_readme_identity_errors", None)
            self.assertIsNotNone(identity_errors)
            assert identity_errors is not None
            return identity_errors(readme, text, [note])

    def test_generated_section_navigation_is_excluded_from_label_checks(self) -> None:
        self.assertEqual(self._errors_for("Section", "Promise"), [])

    def test_wrong_h1_is_rejected(self) -> None:
        self.assertIn(
            "H1 differs from section directory: expected Section",
            self._errors_for("Wrong", "Promise"),
        )

    def test_numbered_manual_link_label_is_rejected(self) -> None:
        self.assertIn(
            "manual note link label contains numeric prefix: 01 Promise",
            self._errors_for("Section", "01 Promise"),
        )

    def test_arbitrary_manual_link_label_is_rejected(self) -> None:
        self.assertIn(
            "manual note link label differs from note title: expected Promise, got Arbitrary",
            self._errors_for("Section", "Arbitrary"),
        )


class RelatedTopicTests(unittest.TestCase):
    def test_existing_non_note_files_and_directories_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo_root = Path(temporary)
            section = repo_root / "notes" / "Section"
            section.mkdir(parents=True)
            note = section / "01 Current.md"
            related = section / "02 Related.md"
            root_readme = repo_root / "README.md"
            assets = repo_root / "assets"
            note.write_text("# Current\n", encoding="utf-8")
            related.write_text("# Related\n", encoding="utf-8")
            root_readme.write_text("# Root\n", encoding="utf-8")
            assets.mkdir()
            body = """- [Related](<./02 Related.md>)
- [Root](<../../README.md>)
- [Assets](<../../assets>)
- [External](https://example.com)
"""
            parser = getattr(check_notes, "related_topic_links", None)
            self.assertIsNotNone(parser)
            assert parser is not None

            targets, errors = parser(note, body, {note.resolve(), related.resolve()})

            self.assertEqual(targets, [related.resolve()])
            self.assertEqual(
                errors,
                [
                    "related topic target is not a note: ../../README.md",
                    "related topic target is not a note: ../../assets",
                    "related topic target is not a note: https://example.com",
                ],
            )


if __name__ == "__main__":
    unittest.main()
