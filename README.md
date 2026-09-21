# Shipwright

Code generator for [Sailor](https://github.com/SailorWebFramework/Sailor). Reads the JSON
specification in [Treasure](https://github.com/SailorWebFramework/Treasure) and emits the
strongly typed Swift under `Sailor/Sources/Sailor/Sources/Generated/` (HTML tags, attributes,
events, element handles, CSS properties and units, Tailwind classes).

## Usage

```bash
pip install -r requirements.txt
python3 main.py build sailor \
    --treasuredir ../Treasure/json \
    --outdir ../Sailor/Sources/Sailor/Sources/Generated
```

Both options default to sibling checkouts (`../Treasure/json` and `./Generated`).

## Layout

| Path | Purpose |
|---|---|
| `main.py` | `click` entry point (`build <target>`). |
| `src/Sailor.py` | Builds the view models for each generated file from Treasure JSON. |
| `src/SailorUtils.py`, `src/Utils.py` | Name conversion (`switch_to_camel`, `parse_type`, …) and formatting helpers. |
| `Templates/` | [chevron](https://github.com/noahmorrison/chevron) (Mustache) templates; `Templates/Sailor/` holds the per-file templates. |
| `tests/` | Golden tests: `tests/fixtures/treasure/` is a committed Treasure snapshot, `tests/fixtures/golden/` the expected Swift output. |

## Tests

```bash
pip install -r requirements-test.txt
pytest tests/
```

The golden tests regenerate from the fixture Treasure JSON and diff every emitted file against
the committed snapshot. When a template change is intentional, refresh the goldens by
re-running codegen into `tests/fixtures/golden/` and committing the diff.

CI also runs a **Codegen → Compile** smoke job that checks out Treasure and Sailor at the same
branch, regenerates Sailor, and runs `swift build` — the single gate that catches drift between
the three repos.
