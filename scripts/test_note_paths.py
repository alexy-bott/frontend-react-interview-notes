from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import note_paths


ROOT = Path(__file__).resolve().parents[1]


class SectionOrderTests(unittest.TestCase):
    def test_new_note_can_be_inserted_at_position_01(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            section = Path(temporary) / "Section"
            section.mkdir()
            old_first = section / "01 First.md"
            new_first = section / "New.md"
            old_first.write_text("# First\n", encoding="utf-8")
            new_first.write_text("# New\n", encoding="utf-8")
            readme = section / "README.md"
            readme.write_text(
                """# Section

<!-- SECTION-NAV:START -->
[Start](<./01 First.md>)
<!-- SECTION-NAV:END -->

## Topics

- [New](<./New.md>)
- [First](<./01 First.md>)
""",
                encoding="utf-8",
            )

            self.assertEqual(
                note_paths.section_order(readme),
                [new_first.resolve(), old_first.resolve()],
            )

    def test_former_first_note_can_move_lower_in_manual_route(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            section = Path(temporary) / "Section"
            section.mkdir()
            first = section / "01 First.md"
            second = section / "02 Second.md"
            third = section / "03 Third.md"
            for note in (first, second, third):
                note.write_text(f"# {note.stem}\n", encoding="utf-8")
            readme = section / "README.md"
            readme.write_text(
                """# Section

<!-- SECTION-NAV:START -->
[Start](<./01 First.md>)
<!-- SECTION-NAV:END -->

## Topics

- [Second](<./02 Second.md>)
- [Third](<./03 Third.md>)
- [First](<./01 First.md>)
""",
                encoding="utf-8",
            )

            self.assertEqual(
                note_paths.section_order(readme),
                [second.resolve(), third.resolve(), first.resolve()],
            )

    def test_duplicate_manual_route_target_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            section = Path(temporary) / "Section"
            section.mkdir()
            first = section / "01 First.md"
            second = section / "02 Second.md"
            first.write_text("# First\n", encoding="utf-8")
            second.write_text("# Second\n", encoding="utf-8")
            readme = section / "README.md"
            readme.write_text(
                """# Section

<!-- SECTION-NAV:START -->
[Start](<./01 First.md>)
<!-- SECTION-NAV:END -->

## Topics

- [First](<./01 First.md>)
- [First again](<./01 First.md>)
- [Second](<./02 Second.md>)
""",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate"):
                note_paths.section_order(readme)


class RewriteInternalLinksTests(unittest.TestCase):
    def test_move_preserves_contextual_label_and_rewrites_only_destination(self) -> None:
        current = ROOT / "notes" / "React" / "Guide.md"
        old_target = ROOT / "notes" / "React" / "useRef.md"
        new_target = ROOT / "notes" / "React" / "13 useRef.md"

        rewritten = note_paths.rewrite_internal_links(
            "See [refs](<./useRef.md>).",
            current,
            current,
            {old_target.resolve(): new_target.resolve()},
        )

        self.assertEqual(rewritten, "See [refs](<./13 useRef.md>).")

    def test_bare_destination_is_wrapped_when_renamed_path_contains_spaces(self) -> None:
        current = ROOT / "notes" / "Section" / "A.md"
        old_target = ROOT / "notes" / "Section" / "B.md"
        new_target = ROOT / "notes" / "Section" / "02 Renamed.md"

        rewritten = note_paths.rewrite_internal_links(
            "See [topic](./B.md).",
            current,
            current,
            {old_target.resolve(): new_target.resolve()},
        )

        self.assertEqual(rewritten, "See [topic](<./02 Renamed.md>).")

    def test_inline_code_with_one_or_more_backticks_is_not_rewritten(self) -> None:
        current = ROOT / "notes" / "Section" / "A.md"
        old_target = ROOT / "notes" / "Section" / "B.md"
        new_target = ROOT / "notes" / "Section" / "Renamed.md"
        text = "Inline: `` `[demo](./B.md)` ``; normal: [demo](./B.md)."

        rewritten = note_paths.rewrite_internal_links(
            text,
            current,
            current,
            {old_target.resolve(): new_target.resolve()},
        )

        self.assertEqual(
            rewritten,
            "Inline: `` `[demo](./B.md)` ``; normal: [demo](./Renamed.md).",
        )

    def test_multiline_inline_code_is_not_rewritten(self) -> None:
        current = ROOT / "notes" / "Section" / "A.md"
        old_target = ROOT / "notes" / "Section" / "B.md"
        new_target = ROOT / "notes" / "Section" / "Renamed.md"
        text = "Inline: ``code\n[demo](./B.md)\nmore``; normal: [demo](./B.md)."

        rewritten = note_paths.rewrite_internal_links(
            text,
            current,
            current,
            {old_target.resolve(): new_target.resolve()},
        )

        self.assertEqual(
            rewritten,
            "Inline: ``code\n[demo](./B.md)\nmore``; normal: [demo](./Renamed.md).",
        )

    def test_different_length_backtick_runs_do_not_form_inline_code(self) -> None:
        current = ROOT / "notes" / "Section" / "A.md"
        old_target = ROOT / "notes" / "Section" / "B.md"
        new_target = ROOT / "notes" / "Section" / "Renamed.md"
        text = "`unclosed [demo](./B.md) ```"

        rewritten = note_paths.rewrite_internal_links(
            text,
            current,
            current,
            {old_target.resolve(): new_target.resolve()},
        )

        self.assertEqual(rewritten, "`unclosed [demo](./Renamed.md) ```")

    def test_empty_link_label_is_rewritten(self) -> None:
        current = ROOT / "notes" / "Section" / "A.md"
        old_target = ROOT / "notes" / "Section" / "B.md"
        new_target = ROOT / "notes" / "Section" / "Renamed.md"

        rewritten = note_paths.rewrite_internal_links(
            "[](./B.md)",
            current,
            current,
            {old_target.resolve(): new_target.resolve()},
        )

        self.assertEqual(rewritten, "[](./Renamed.md)")

    def test_external_destination_classifier_covers_uri_and_protocol_relative_links(self) -> None:
        classifier = getattr(note_paths, "is_external_destination", None)
        self.assertIsNotNone(classifier)
        assert classifier is not None

        for destination in ("#part", "tel:+79990000000", "custom+scheme:value", "//cdn.example/app.js"):
            with self.subTest(destination=destination):
                self.assertTrue(classifier(destination))
        self.assertFalse(classifier("./01 Note.md"))


if __name__ == "__main__":
    unittest.main()
