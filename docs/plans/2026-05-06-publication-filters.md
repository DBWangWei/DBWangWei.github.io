# Publication Filters Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add clickable tag and venue filters to both generated publication pages so visitors can filter by one tag, one venue, or both together, and clear filters to restore all papers.

**Architecture:** Extend the shared publications rendering pipeline so it emits filter controls, normalized `data-*` attributes on each publication entry, and a small inline client-side script. Keep the feature as progressive enhancement: without JavaScript the pages still render all publications normally, and with JavaScript the filters update entry and year-header visibility in place.

**Tech Stack:** Python publication generator, generated Markdown with embedded HTML/JS, MkDocs, pytest, shared CSS in `docs/stylesheets/publications.css`

---

### Task 1: Add generator tests for filter markup and metadata

**Files:**
- Modify: `tests/publications/test_publications_pipeline.py`
- Reference: `tools/publications/publications_lib.py`

**Step 1: Write the failing test**

Add assertions to `test_build_publications_generates_cache_report_and_pages` or add a focused new test that verifies generated page output contains:
- a filter container such as `pub-filters`
- a clear button/control
- tag filter chips for page-specific tags
- venue filter chips for page-specific venues
- `data-tags`, `data-venue`, and `data-year` attributes on rendered publication entries

Example assertions:

```python
assert 'class="pub-filters"' in all_md
assert 'data-filter-group="tags"' in all_md
assert 'data-filter-group="venues"' in all_md
assert 'data-tags="ann high-dim"' in selected_md
assert 'data-venue="vldb"' in selected_md
assert 'data-year="2026"' in selected_md
assert 'Clear filters' in all_md
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/publications/test_publications_pipeline.py -k filter -v
```

Expected: FAIL because the current generator does not emit filter UI or metadata.

**Step 3: Write minimal implementation**

Do not implement everything yet; only add the test first.

**Step 4: Run test to verify it fails in the expected way**

Run:
```bash
pytest tests/publications/test_publications_pipeline.py -k filter -v
```

Expected: FAIL with missing filter markup or missing `data-*` attributes.

**Step 5: Commit**

```bash
git add tests/publications/test_publications_pipeline.py
git commit -m "test: cover publication filter markup"
```

### Task 2: Add normalization helpers and filter UI rendering

**Files:**
- Modify: `tools/publications/publications_lib.py`
- Test: `tests/publications/test_publications_pipeline.py`

**Step 1: Write the failing test for normalization and page-specific options**

Add or extend a test so it verifies:
- venue labels are preserved for display
- normalized values are lowercase slug-like strings for matching
- selected page only includes tags/venues actually present on selected records

Example expectations:

```python
assert 'data-value="vldb"' in selected_md
assert 'data-value="emnlp"' in all_md
assert 'ACL Findings' not in selected_md or only appears if a selected paper uses it
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/publications/test_publications_pipeline.py::test_build_publications_generates_cache_report_and_pages -v
```

Expected: FAIL because no normalization helpers or filter toolbar exist.

**Step 3: Write minimal implementation**

In `tools/publications/publications_lib.py`, add small helpers such as:

```python
def normalize_filter_value(value: str) -> str:
    value = normalize_whitespace(value).casefold()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value


def render_filter_chip(group: str, label: str) -> str:
    value = normalize_filter_value(label)
    return (
        f'<button type="button" class="pub-filter-chip" '
        f'data-filter-group="{group}" data-value="{escape(value, quote=True)}">'
        f'{escape(label)}</button>'
    )
```

Add a helper to collect page-local unique tags and venues and render a top-of-page filter block.

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/publications/test_publications_pipeline.py::test_build_publications_generates_cache_report_and_pages -v
```

Expected: PASS for filter toolbar and normalized chip output.

**Step 5: Commit**

```bash
git add tools/publications/publications_lib.py tests/publications/test_publications_pipeline.py
git commit -m "feat: render publication filter controls"
```

### Task 3: Add entry metadata and inline filtering script

**Files:**
- Modify: `tools/publications/publications_lib.py`
- Test: `tests/publications/test_publications_pipeline.py`

**Step 1: Write the failing test for script presence and matching metadata**

Add assertions for:
- filter script marker or function names in generated Markdown
- entry wrapper metadata needed by JS
- year heading hooks for hide/show logic

Example assertions:

```python
assert 'data-publication-entry="true"' in all_md
assert 'data-publication-year="2026"' in all_md
assert 'function applyPublicationFilters()' in all_md
assert 'data-selected-tag' in all_md
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/publications/test_publications_pipeline.py -k publications_generates_cache_report_and_pages -v
```

Expected: FAIL because script and metadata are not yet emitted.

**Step 3: Write minimal implementation**

Update `render_record` so each publication entry includes normalized metadata, for example:

```python
tag_values = " ".join(normalize_filter_value(area) for area in record.get("areas", []))
venue_value = normalize_filter_value(record["venue"])

'<div class="pub-entry" data-publication-entry="true" '
 f'data-tags="{escape(tag_values, quote=True)}" '
 f'data-venue="{escape(venue_value, quote=True)}" '
 f'data-year="{record["year"]}">'
```

Update year headings so they can be targeted by JavaScript.

Add a small inline script renderer, for example a helper that returns a `<script>` block that:
- stores one selected tag and one selected venue
- toggles active chip classes
- shows entries when both selected filters match
- hides year headers with no visible entries
- clears all selections when clear is clicked

Keep it small and page-local. Do not introduce external JS files unless clearly necessary.

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/publications/test_publications_pipeline.py::test_build_publications_generates_cache_report_and_pages -v
```

Expected: PASS with filter script and entry metadata present.

**Step 5: Commit**

```bash
git add tools/publications/publications_lib.py tests/publications/test_publications_pipeline.py
git commit -m "feat: add publication page filtering behavior"
```

### Task 4: Style the filter UI and hidden states

**Files:**
- Modify: `docs/stylesheets/publications.css`
- Test: `tests/publications/test_build_smoke.py`

**Step 1: Write the failing test**

Add assertions in `tests/publications/test_build_smoke.py` that the stylesheet contains rules for the new filter UI and hidden states, for example:

```python
assert ".pub-filters" in css
assert ".pub-filter-chip" in css
assert ".pub-filter-chip.is-active" in css
assert "[hidden]" in css or ".is-hidden" in css
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/publications/test_build_smoke.py -k css -v
```

Expected: FAIL because the filter classes are not styled yet.

**Step 3: Write minimal implementation**

Extend `docs/stylesheets/publications.css` with styles for:
- `.pub-filters`
- `.pub-filter-group`
- `.pub-filter-chip`
- `.pub-filter-chip.is-active`
- `.pub-filter-clear`
- optional `.pub-filter-status`
- hidden state for filtered-out list items or entries

Keep the visual language close to the current `pub-tag` styles and ensure responsive wrapping.

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/publications/test_build_smoke.py -k css -v
```

Expected: PASS.

**Step 5: Commit**

```bash
git add docs/stylesheets/publications.css tests/publications/test_build_smoke.py
git commit -m "style: add publication filter styles"
```

### Task 5: Regenerate pages and verify pipeline output

**Files:**
- Modify (generated): `docs/intro/publications.md`
- Modify (generated): `docs/intro/publications_selected.md`
- Modify (generated/build output as needed): `site/...`
- Run against: `tools/publications/build_publications.py`

**Step 1: Write the failing verification expectation**

No new test file needed if existing tests cover generation. Ensure there are assertions that generated pages include filter markup after rebuild.

**Step 2: Run the publication build**

Run:
```bash
python3 tools/publications/build_publications.py
```

Expected before full implementation: generated pages may still be missing parts or not yet reflect final behavior.

**Step 3: Write minimal implementation adjustments if rebuild exposes gaps**

If the generated Markdown structure is awkward for filtering, make the smallest generator changes necessary so the rebuilt pages include:
- top filter controls
- per-entry metadata
- filter script

**Step 4: Re-run build and verify output**

Run:
```bash
python3 tools/publications/build_publications.py
```

Expected: PASS with regenerated `docs/intro/publications.md` and `docs/intro/publications_selected.md` containing filter controls.

**Step 5: Commit**

```bash
git add tools/publications/publications_lib.py docs/intro/publications.md docs/intro/publications_selected.md
git commit -m "build: regenerate publication pages with filters"
```

### Task 6: Run focused tests and smoke build

**Files:**
- Test: `tests/publications/test_publications_pipeline.py`
- Test: `tests/publications/test_build_smoke.py`
- Build: `mkdocs.yml`

**Step 1: Run focused publication tests**

Run:
```bash
pytest tests/publications/test_publications_pipeline.py tests/publications/test_build_smoke.py -v
```

Expected: PASS.

**Step 2: Run MkDocs build smoke test**

Run:
```bash
mkdocs build
```

Expected: PASS and regenerated site output without template or markdown errors.

**Step 3: Fix only failures uncovered by verification**

If tests or build fail, make the smallest corrections in:
- `tools/publications/publications_lib.py`
- `docs/stylesheets/publications.css`
- tests only if expectations were wrong

**Step 4: Re-run verification**

Run:
```bash
pytest tests/publications/test_publications_pipeline.py tests/publications/test_build_smoke.py -v && mkdocs build
```

Expected: PASS.

**Step 5: Commit**

```bash
git add tools/publications/publications_lib.py docs/stylesheets/publications.css tests/publications/test_publications_pipeline.py tests/publications/test_build_smoke.py docs/intro/publications.md docs/intro/publications_selected.md site
git commit -m "feat: add publication tag and venue filters"
```
