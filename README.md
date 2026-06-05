# weiwcs.github.io

This repository contains the source for Wei Wang's academic homepage, built with MkDocs + Material and deployed via GitHub Pages.

## Project structure

- `mkdocs.yml` — site configuration and navigation
- `docs/` — source Markdown, assets, stylesheets, teaching/research pages
- `site/` — generated static site output
- `data/publications/` — bibliography source, curated metadata, generated cache/report
- `tools/publications/` — publication sync/bootstrap/build scripts
- `.github/workflows/ci.yml` — CI build and deployment workflow

## Publications pipeline

The publications pages are generated from a small pipeline. Do **not** manually maintain `docs/intro/publications_selected.md` or `docs/intro/publications.md`.

### Source layers

1. External scholarly source:
   - `/Users/weiwang/weiw/Research/=Grant.Proposal/my-bib/WeiWang.bib`
2. Repo-local merged bibliography:
   - `data/publications/merged.bib`
3. Curated website metadata:
   - `data/publications/overrides.json`
4. Generated artifacts:
   - `data/publications/publications.cache.json`
   - `data/publications/publications.report.json`
   - `docs/intro/publications_selected.md`
   - `docs/intro/publications.md`

### Main scripts

- `python3 tools/publications/sync_bib.py`
  - merges the external BibTeX source into `data/publications/merged.bib`
  - records sync collisions in `data/publications/publications.report.json`
- `python3 tools/publications/bootstrap_selected_metadata.py`
  - bootstraps selected-paper metadata from the old selected page
  - mainly useful for migration/recovery
- `python3 tools/publications/build_publications.py`
  - generates the cache, report, selected-publications page, and all-publications page

## How to add or revise a publication

### Case 1: the paper already exists in the external BibTeX source

1. Update the external BibTeX file if needed:
   - `/Users/weiwang/weiw/Research/=Grant.Proposal/my-bib/WeiWang.bib`
2. Sync it into the repo-local bibliography:

```bash
python3 tools/publications/sync_bib.py
```

3. Add or revise website-specific metadata in:
   - `data/publications/overrides.json`
4. Regenerate the site publication artifacts:

```bash
python3 tools/publications/build_publications.py
```

### Case 2: the paper is not yet in the external BibTeX source

1. Add the BibTeX entry directly to:
   - `data/publications/merged.bib`
2. Add or revise the matching metadata in:
   - `data/publications/overrides.json`
3. Rebuild generated outputs:

```bash
python3 tools/publications/build_publications.py
```

### Website metadata fields in `overrides.json`

Each paper is keyed by BibTeX citation key. Common fields:

- `selected`: `true` or `false`
- `areas`: 1–3 short tags such as `DB`, `LLM`, `AI4S`, `ANN`, `Graph`, `DL`, `XAI`, `PDE`, `Theory`, `AdvML`, `App`, `High-Dim`
- `pdf`: local repo path or external URL
- `url`: canonical landing page URL
- `note`: optional short display note such as award text

Example:

```json
{
  "fervvac:vldb26-IndexSelectionAKNN": {
    "selected": true,
    "areas": ["ANN", "High-Dim"],
    "pdf": "docs/papers/2026/index-selection-aknn.pdf",
    "url": "https://example.org/project-page",
    "note": "Best Paper Candidate"
  }
}
```

### PDFs

Preferred location for repo-hosted PDFs:

- `docs/papers/<year>/...`

Examples:

- `docs/papers/2026/index-selection-aknn.pdf`
- `docs/papers/2025/my-paper.pdf`

If a PDF is not available yet, omit `pdf` and add it later.

### Important rule

After changing publication data, always regenerate:

```bash
python3 tools/publications/build_publications.py
```

Then inspect:

- `data/publications/publications.report.json`

Pay attention to:
- `sync_duplicates`
- `duplicates`
- `inferred_areas`
- `missing_local_pdfs`

## Local setup

Install dependencies:

```bash
pip install -r requirements.txt
pip install mkdocs-material
```

## How to test locally

Run publication-focused tests:

```bash
pytest tests/publications/test_publications_pipeline.py -v
pytest tests/publications/test_build_smoke.py -v
```

Run all steps manually:

```bash
python3 tools/publications/build_publications.py
mkdocs build
```

## How to view locally

### Option 1: serve the site locally

```bash
python3 tools/publications/build_publications.py
mkdocs serve
```

Then open the local MkDocs URL shown in the terminal.

### Option 2: build static output only

```bash
python3 tools/publications/build_publications.py
mkdocs build
```

Then inspect generated files such as:

- `site/intro/publications_selected/index.html`
- `site/intro/publications/index.html`

## How to update GitHub

### Recommended workflow

1. Regenerate publications:

```bash
python3 tools/publications/build_publications.py
```

2. Build locally:

```bash
mkdocs build
```

3. Run tests if needed:

```bash
pytest tests/publications/test_publications_pipeline.py -v
pytest tests/publications/test_build_smoke.py -v
```

4. Commit the updated source and generated files.
5. Push to `main`.

GitHub Actions will then:
- install dependencies
- rebuild publications
- run `mkdocs build`
- deploy `site/` to GitHub Pages

### CI workflow

Defined in:
- `.github/workflows/ci.yml`

### Optional helper scripts

The repository also contains:
- `__update_web.sh`
- `__update_web_no_del.sh`

These are local helper scripts for copying the built site to a separate local GitHub Pages repository checkout.

## Notes

- Publication pages reuse `docs/stylesheets/publications.css`.
- Navigation paths remain stable:
  - `intro/publications_selected.md`
  - `intro/publications.md`
- The build report is the first place to check when a publication update looks wrong.

