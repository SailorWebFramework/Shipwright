"""
Shipwright test configuration and shared fixtures.
"""
import os
import sys
import subprocess
import shutil
import tempfile
import pytest

# Make src/ importable
SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, SRC_DIR)

TESTS_DIR = os.path.dirname(__file__)
FIXTURES_DIR = os.path.join(TESTS_DIR, "fixtures")
TREASURE_DIR = os.path.join(FIXTURES_DIR, "treasure")
EXPECTED_DIR = os.path.join(FIXTURES_DIR, "expected")
MAIN_PY = os.path.join(os.path.dirname(__file__), "..", "main.py")


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
        cwd=os.path.dirname(MAIN_PY),
    )
    if result.returncode != 0:
        pytest.fail(
            f"Shipwright codegen failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return outdir
