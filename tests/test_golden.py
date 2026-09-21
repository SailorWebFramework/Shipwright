"""
Shipwright golden-file tests.

Compares fresh codegen output (from fixture treasure snapshot) against the
committed expected/ directory.  Any diff means the template or data changed
in a way that wasn't intentionally captured.

Run with --update-goldens to regenerate the expected/ files in place.
"""
import os
import pytest

from conftest import EXPECTED_DIR


def _collect_expected_files():
    """Return list of relative paths for all files in fixtures/expected/."""
    paths = []
    for dirpath, _, filenames in os.walk(EXPECTED_DIR):
        for fname in filenames:
            abs_path = os.path.join(dirpath, fname)
            rel = os.path.relpath(abs_path, EXPECTED_DIR)
            paths.append(rel)
    return sorted(paths)


@pytest.mark.parametrize("rel_path", _collect_expected_files())
def test_golden_file(rel_path, generated_dir, update_goldens):
    """Each generated file must exactly match its committed golden."""
    if update_goldens:
        pytest.skip("--update-goldens: goldens were regenerated, skipping comparison")

    expected_path = os.path.join(EXPECTED_DIR, rel_path)
    actual_path = os.path.join(generated_dir, rel_path)

    assert os.path.exists(actual_path), (
        f"Generated file missing: {rel_path}\n"
        f"(Run with --update-goldens to regenerate expected/)"
    )

    with open(expected_path, "r") as f:
        expected = f.read()
    with open(actual_path, "r") as f:
        actual = f.read()

    assert actual == expected, (
        f"Golden mismatch for {rel_path}\n"
        f"Run `pytest --update-goldens` to accept new output.\n"
        f"--- expected\n+++ actual\n"
        + _unified_diff(expected, actual, rel_path)
    )


def test_no_extra_generated_files(generated_dir, update_goldens):
    """Codegen must not produce files absent from the committed golden set."""
    if update_goldens:
        pytest.skip("--update-goldens: goldens were regenerated, skipping comparison")

    expected_files = set(_collect_expected_files())
    actual_files = set()
    for dirpath, _, filenames in os.walk(generated_dir):
        for fname in filenames:
            abs_path = os.path.join(dirpath, fname)
            rel = os.path.relpath(abs_path, generated_dir)
            actual_files.add(rel)

    extra = actual_files - expected_files
    assert not extra, (
        f"{len(extra)} extra generated file(s) not in expected/:\n"
        + "\n".join(f"  {p}" for p in sorted(extra)[:20])
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _unified_diff(expected: str, actual: str, label: str) -> str:
    import difflib
    diff = difflib.unified_diff(
        expected.splitlines(keepends=True),
        actual.splitlines(keepends=True),
        fromfile=f"expected/{label}",
        tofile=f"actual/{label}",
        n=3,
    )
    lines = list(diff)
    if len(lines) > 60:
        lines = lines[:60] + [f"... ({len(lines) - 60} more lines)\n"]
    return "".join(lines)
