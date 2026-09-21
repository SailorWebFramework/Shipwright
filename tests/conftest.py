"""
Shipwright test configuration and shared fixtures.
"""
import os
import sys
import subprocess
import shutil
import tempfile
import pytest

# All paths are normalised to absolute so subprocess.run and os.path.exists
# behave identically on macOS and Linux regardless of how pytest was invoked.
_HERE = os.path.dirname(os.path.abspath(__file__))
SHIPWRIGHT_ROOT = os.path.normpath(os.path.join(_HERE, ".."))

# Make src/ importable in this process
SRC_DIR = os.path.join(SHIPWRIGHT_ROOT, "src")
sys.path.insert(0, SRC_DIR)

TESTS_DIR = _HERE
FIXTURES_DIR = os.path.join(TESTS_DIR, "fixtures")
TREASURE_DIR = os.path.join(FIXTURES_DIR, "treasure")
EXPECTED_DIR = os.path.join(FIXTURES_DIR, "expected")
MAIN_PY = os.path.join(SHIPWRIGHT_ROOT, "main.py")


def pytest_addoption(parser):
    parser.addoption(
        "--update-goldens",
        action="store_true",
        default=False,
        help="Regenerate golden files from fixture treasure instead of comparing.",
    )


@pytest.fixture(scope="session")
def update_goldens(request):
    return request.config.getoption("--update-goldens")


@pytest.fixture(scope="session")
def generated_dir(update_goldens, tmp_path_factory):
    """
    Run Shipwright codegen against the fixture treasure snapshot.

    If --update-goldens is set, writes output directly to fixtures/expected/
    and returns that path.  Otherwise writes to a temp dir so the comparison
    tests can diff against fixtures/expected/.
    """
    if update_goldens:
        outdir = EXPECTED_DIR
        shutil.rmtree(outdir, ignore_errors=True)
        os.makedirs(outdir, exist_ok=True)
    else:
        outdir = str(tmp_path_factory.mktemp("generated"))

    result = subprocess.run(
        [sys.executable, MAIN_PY, "build", "sailor",
         "--outdir", outdir,
         "--treasuredir", TREASURE_DIR],
        capture_output=True,
        text=True,
        cwd=SHIPWRIGHT_ROOT,  # normalised absolute path — not os.path.dirname(MAIN_PY)
    )

    # Fail loudly with full diagnostics if codegen produced nothing or exited non-zero.
    # An empty outdir with returncode=0 means Sailor.build() returned early (e.g. treasure
    # dir not found). We treat that as a failure rather than silently testing nothing.
    generated_files = []
    for dirpath, _, filenames in os.walk(outdir):
        generated_files.extend(filenames)

    if result.returncode != 0 or not generated_files:
        pytest.fail(
            f"Shipwright codegen {'failed' if result.returncode != 0 else 'produced no output'} "
            f"(exit {result.returncode})\n"
            f"  cwd:          {SHIPWRIGHT_ROOT}\n"
            f"  MAIN_PY:      {MAIN_PY}\n"
            f"  outdir:       {outdir}\n"
            f"  TREASURE_DIR: {TREASURE_DIR}\n"
            f"  treasure exists: {os.path.exists(TREASURE_DIR)}\n"
            f"  stdout: {result.stdout!r}\n"
            f"  stderr: {result.stderr!r}"
        )
    return outdir
