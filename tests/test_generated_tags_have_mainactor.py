"""
Verify that every generated HTML tag struct is annotated with @MainActor.

Swift 6 strict concurrency requires all DOM-touching types to be @MainActor.
A tag struct missing the annotation will cause actor isolation errors in
consumer code.

Rule: every file in Tags/ that defines `public struct <Name>:` must have
`@MainActor` immediately before `public struct`.
"""
import os
import re
import pytest

from conftest import EXPECTED_DIR

TAGS_DIR = os.path.join(EXPECTED_DIR, "Tags")

# Pattern: @MainActor (possibly with other attrs before) then public struct Name:
_MAINACTOR_STRUCT = re.compile(r"@MainActor\s+public\s+struct\s+\w+\s*:")
# Pattern: public struct Name: (without @MainActor on same/prior line)
_BARE_STRUCT = re.compile(r"(?<!@MainActor\s)public\s+struct\s+\w+\s*:")


def _tag_swift_files():
    if not os.path.isdir(TAGS_DIR):
        return []
    result = []
    for fname in os.listdir(TAGS_DIR):
        if fname.endswith(".swift"):
            result.append((fname, os.path.join(TAGS_DIR, fname)))
    return sorted(result)


@pytest.mark.parametrize("fname,abs_path", _tag_swift_files())
def test_tag_struct_has_mainactor(fname, abs_path):
    """Every HTML tag struct must be annotated with @MainActor."""
    with open(abs_path, "r") as f:
        content = f.read()

    # Check that @MainActor appears before a public struct declaration
    if not _MAINACTOR_STRUCT.search(content):
        # Does the file even have a public struct?  (GlobalAttributeGroup etc. may not)
        bare = _BARE_STRUCT.findall(content)
        if bare:
            pytest.fail(
                f"{fname}: public struct declaration missing @MainActor annotation.\n"
                f"Found: {bare[:3]}"
            )
        else:
            pytest.skip(f"{fname}: no public struct declaration found — skipping")
