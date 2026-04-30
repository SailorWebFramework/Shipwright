# Shipwright Codegen Test Report

**Date:** 2026-03-14
**Branch:** feature-fin
**Python:** 3.14.3 | **Dependencies:** chevron 0.14.0, click 8.3.1

---

## 1. Generator Run Result: FAILED

The generator crashes during `buildUnits()` with a `KeyError: 'names'` when processing the `GridAutoFlow` unit type.

```
File "src/Sailor.py", line 231, in <lambda>
    "format": SailorUtils.put_formatted(v[1]["format"], v[1]["names"], types=v[1]["values"]) if "format" in v[1] else "",
KeyError: 'names'
```

Tags were generated successfully before the crash. Units, CSS properties, and other outputs were not generated.

---

## 2. Issues Found

### CRITICAL: Crashes the generator

#### Issue 1 — `GridAutoFlow` cases have `format` but no `names`

**Location:** `Treasure/json/units.json` — `GridAutoFlow.row-dense` and `GridAutoFlow.column-dense`

These cases specify a `format` string but omit `names` and `values`. The `format_cases` lambda in `Sailor.buildUnits()` unconditionally accesses `v[1]["names"]` when `"format" in v[1]`, causing a `KeyError`.

**Fix (Treasure):** Add empty `names`/`values` arrays, or remove the `format` key and rely on the case name:

```json
"row-dense": {
    "description": "Fill rows densely.",
    "format": "row dense"
}
```

Should become either:
- Remove `format` and rename the case to output `row-dense` (the default behavior outputs the case name)
- Or add: `"names": [], "values": []` so `put_formatted` receives valid inputs

**Fix (Shipwright):** Make `buildUnits` resilient — if `format` exists but `names` doesn't, treat it as a static format string:

```python
# In format_cases lambda, line 231:
"format": SailorUtils.put_formatted(v[1]["format"], v[1].get("names", []), types=v[1].get("values")) if "format" in v[1] else "",
```

**Recommendation:** Fix both — Treasure should be explicit, and Shipwright should be defensive.

---

### HIGH: Produces wrong output

#### Issue 2 — `font-*.family` format is `"SEQ,"` instead of `"#SEQ,"`

**Location:** `Treasure/json/properties.json` line 957

The format string is `"SEQ,"` (missing the `#` prefix). The `put_formatted` method checks `data[0:4] == "#SEQ"` to detect sequence formats. Without the `#`, it falls through to regular template replacement, which will produce incorrect Swift interpolation code — `SEQ,` will appear as a literal string in the output.

**Fix:** Change `"format": "SEQ,"` to `"format": "#SEQ,"` in properties.json.

#### Issue 3 — `grid:0` has dual `#SEQ` format that `put_formatted` can't handle

**Location:** `Treasure/json/properties.json` line 1903

```json
"format": "#SEQ  / #SEQ "
```

This format has TWO `#SEQ` markers for two separate sequence parameters (`templateRows` and `templateColumns`). The current `put_formatted` implementation only handles a single `#SEQ` at position `data[0:4]`. The second `#SEQ` will remain as literal text `#SEQ ` in the generated Swift code.

**Fix (Shipwright):** Extend `put_formatted` to handle multiple `#SEQ` markers. Each `#SEQ` should consume the next sequence-typed parameter in order:

```python
# Proposed approach: replace each #SEQ with the corresponding sequence name
import re
seq_names = [name for name, typ in zip(real_names, types or []) if 'sequence[' in str(typ)]
for seq_name in seq_names:
    data = data.replace(
        '#SEQ',
        f'\\({seq_name}.map {{ $0.description }}.joined(separator: "{separator}"))',
        1  # replace only first occurrence
    )
```

Note: The separator character is currently taken from `data[4]` (the char after `#SEQ`). With multiple `#SEQ` markers, each needs its own separator parsed from the character following it.

---

### MEDIUM: Functional but should be validated

#### Issue 4 — `sequence[...]` values in unit cases (units used as variadic Swift params)

**Affected units:** `Quotes.with`, `GridTrackList.tracks`, `GridTemplateAreas.areas`

These unit cases use `sequence[Unit.Pair]`, `sequence[Unit.GridTrackSize]`, and `sequence[String]` as value types. The `convert_type()` method converts these to Swift variadic parameters (e.g., `Unit.Pair...`), and the `#SEQ` format correctly generates `.joined(separator:)` calls.

**Status:** Should work correctly once Issue 1 is fixed. The `#SEQ` + `sequence[...]` combination is already handled by the existing code path.

#### Issue 5 — `put_formatted` called from `buildUnits` without `real_names` param

When `buildUnits` calls `put_formatted(format, names, types=values)`, it doesn't pass `real_names`. This means `real_names` defaults to `names` (the raw JSON names), which haven't been camelCase-converted yet. This is fine for units since unit case args use the raw name for Swift interpolation, but it's inconsistent with how properties pass both `names` and `formatted_names`.

**Status:** Works but could cause subtle bugs if unit names contain hyphens or special characters. Low risk since most unit arg names are simple (`value`, `x`, `y`, etc.).

---

## 3. New Patterns Analysis

### Time unit type (s, ms) — OK
Standard pattern: cases with `values`, `names`, `format`. No issues. Follows the exact same structure as `Length` (px, em, etc.).

### TimingFunction unit type — OK
Mix of simple cases (`ease`, `linear`) and parameterized cases (`cubic-bezier` with 4 Double params, `steps` with Int + optional StepPosition). All follow existing patterns. The `steps:0` / `steps:1` variant pattern is already used elsewhere (e.g., `BoxShadow with:0/with:1`).

### Animation shorthand property — OK (with caveat)
`animation:0` has 8 parameters — the most of any property. The template handles arbitrary parameter counts via `{{#typedNames}}` iteration. No structural issue, but the generated Swift function signature will be very long. The `animation:1` and `animation:2` variants provide shorter alternatives.

### Grid template properties — BLOCKED by Issues 1 and 3
- `grid-template-areas` uses `Unit.GridTemplateAreas` — standard pattern, will work once Issue 1 is fixed.
- `grid-template-columns/rows` with `sequence[Unit.GridTrackSize]` — standard `#SEQ` pattern, will work.
- `grid:0` shorthand with dual sequences — blocked by Issue 3 (multi-`#SEQ`).
- `GridAutoFlow` unit — blocked by Issue 1 (missing `names`).

### SVG properties (clip-rule, paint-order, pointer-events) — OK
These use simple `Unit.FillRule`, `Unit.PaintOrder`, `Unit.PointerEvents` types with standard `{{value}}` formats. No new patterns.

### `sequence[...]` types in properties — OK (existing pattern)
Properties like `box-shadow`, `background-image`, `transition-property`, `counter-*`, and `transform` all use `sequence[Unit.X]` types with `#SEQ` format. This pattern has been working since earlier property additions.

---

## 4. Required Template Changes

**No template changes needed.** The Mustache templates (`Unit+Enum.mustache`, `Style+Property.mustache`) are generic enough to handle all new patterns. The issues are in:

1. **Treasure JSON data** (Issues 1 and 2) — data entry errors
2. **Shipwright Python codegen** (Issues 1 and 3) — `put_formatted` and `format_cases` need hardening

---

## 5. Recommended Fixes (Priority Order)

| Priority | Issue | Where | Fix |
|----------|-------|-------|-----|
| P0 | GridAutoFlow missing `names` | Treasure + Shipwright | Add names/values to JSON; add `.get()` fallback in Python |
| P0 | font-family `SEQ,` → `#SEQ,` | Treasure | One-char fix in properties.json |
| P1 | Multi-`#SEQ` support | Shipwright | Extend `put_formatted` to handle N sequence params |
| P2 | Defensive `names`/`values` access | Shipwright | Use `.get()` throughout `format_cases` |

---

## 6. Generated Output (Partial)

Before the crash, the generator successfully created tag files in `dev/Generated/Tags/`:
- All HTML tag Swift files were generated correctly
- Unit generation failed at `GridAutoFlow`, preventing all subsequent steps
