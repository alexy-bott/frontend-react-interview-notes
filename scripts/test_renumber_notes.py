from __future__ import annotations

import unittest
from pathlib import Path

from scripts.renumber_notes import apply_moves, validate_moves


class ValidateMovesTests(unittest.TestCase):
    def test_rejects_source_escaping_notes_root_with_parent_directory(self) -> None:
        root = (Path(__file__).resolve().parents[1] / "notes").resolve()
        escaped_source = root / ".." / "outside" / "source.md"
        target = root / "01 Target.md"

        with self.assertRaises(ValueError):
            validate_moves({escaped_source: target}, root)
        with self.assertRaises(ValueError):
            apply_moves({escaped_source: target}, root)


if __name__ == "__main__":
    unittest.main()
