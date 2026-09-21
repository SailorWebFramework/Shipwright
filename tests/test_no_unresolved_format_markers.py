"""
Verify that no generated Swift file contains unresolved Mustache markers
or raw format-string tokens that should have been substituted at codegen time.

Patterns checked:
  1. Mustache tags:  {{...}}  or  {{{...}}}  — template not fully rendered
  2. Raw #SEQ token — put_formatted failed to substitute a sequence placeholder
  3. Raw {{name}} placeholder — format string not interpolated
"""
import os
import re
import pytest

from conftest import EXPECTED_DIR

# ---------------------------------------------------------------------------
# Known files with unresolved markers — tracked as data bugs in GitHub issues
# These are Treasure JSON format/names mismatches that survive into the output.
# All previously known issues (#4 border-*, #5 Integer/BackgroundSize) have been
# fixed.  This set is intentionally empty; leave it here so the xfail branch
# below is easy to reinstate if a new regression appears.
# ---------------------------------------------------------------------------
KNOWN_UNRESOLVED_MARKER_FILES: set = set()


def _all_swift_files(base_dir: str):
    """Yield (rel_path, abs_path) for every .swift file under base_dir."""
    for dirpath, _, filenames in os.walk(base_dir):
        for fname in filenames:
            if fname.endswith(".swift"):
                abs_path = os.path.join(dirpath, fname)
                rel = os.path.relpath(abs_path, base_dir)
                yield rel, abs_path


# Patterns that must NOT appear in generated output
_UNRESOLVED_PATTERNS = [
    (re.compile(r"\{\{\{[^}]+\}\}\}"), "triple-brace Mustache tag"),
    (re.compile(r"\{\{[^}]+\}\}"), "double-brace Mustache tag"),
    (re.compile(r"#SEQ\b"), "unresolved #SEQ marker"),
]


@pytest.mark.parametrize("rel_path,abs_path", list(_all_swift_files(EXPECTED_DIR)))
def test_no_unresolved_markers(rel_path, abs_path):
    """Generated Swift files must not contain unresolved template markers."""
    with open(abs_path, "r") as f:
        content = f.read()

    violations = []
    for pattern, label in _UNRESOLVED_PATTERNS:
        matches = pattern.findall(content)
        if matches:
            violations.append((label, matches[:3]))

    if violations:
        if rel_path in KNOWN_UNRESOLVED_MARKER_FILES:
            pytest.xfail(
                f"Known data bug — unresolved markers in {rel_path} "
                f"(tracked in GitHub issues): "
                + "; ".join(f"[{l}]: {m}" for l, m in violations)
            )
        assert not violations, (
            f"{rel_path} contains unresolved markers:\n"
            + "\n".join(f"  [{label}]: {m}" for label, m in violations)
        )
