import json
import subprocess
from pathlib import Path


def test_repo_publication_artifacts_exist():
    assert Path("data/publications/merged.bib").exists()
    assert Path("data/publications/overrides.json").exists()


def test_publication_build_is_wired_into_repo_workflows():
    requirements = Path("requirements.txt").read_text(encoding="utf-8")
    ci_workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    update_script = Path("__update_web.sh").read_text(encoding="utf-8")
    update_script_no_del = Path("__update_web_no_del.sh").read_text(encoding="utf-8")

    assert "bibtexparser" in requirements
    assert "build_publications.py" in ci_workflow
    assert "build_publications.py" in update_script
    assert "build_publications.py" in update_script_no_del
    assert 'mkdocs build 2>&1 || { echo "Error running mkdocs build: $?"; exit 1; }' in update_script
    assert 'mkdocs build 2>&1 || { echo "Error running mkdocs build: $?"; exit 1; }' in update_script_no_del


def test_repo_publication_pages_build_from_repo_data(tmp_path):
    cache_path = tmp_path / "publications.cache.json"
    report_path = tmp_path / "publications.report.json"
    selected_page = tmp_path / "publications_selected.md"
    all_page = tmp_path / "publications.md"

    subprocess.run(
        [
            "python3",
            "tools/publications/build_publications.py",
            "--cache",
            str(cache_path),
            "--report",
            str(report_path),
            "--selected-page",
            str(selected_page),
            "--all-page",
            str(all_page),
        ],
        check=True,
    )

    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    selected_md = selected_page.read_text(encoding="utf-8")
    all_md = all_page.read_text(encoding="utf-8")

    assert cache["summary"]["all_count"] > 0
    assert cache["summary"]["selected_count"] > 0
    assert selected_md.count('<div class="pub-entry" data-publication-entry="true"') == cache["summary"]["selected_count"]
    assert all_md.count('<div class="pub-entry" data-publication-entry="true"') == cache["summary"]["all_count"]


def test_repo_all_2026_publications_are_selected(tmp_path):
    cache_path = tmp_path / "publications.cache.json"
    report_path = tmp_path / "publications.report.json"

    subprocess.run(
        [
            "python3",
            "tools/publications/build_publications.py",
            "--cache",
            str(cache_path),
            "--report",
            str(report_path),
        ],
        check=True,
    )

    records = json.loads(cache_path.read_text(encoding="utf-8"))["records"]
    records_2026 = [record for record in records if record["year"] == 2026]
    assert records_2026
    assert all(record["selected"] for record in records_2026)


def test_publication_filter_javascript_is_loaded_globally():
    mkdocs = Path("mkdocs.yml").read_text(encoding="utf-8")
    script = Path("docs/javascripts/publication-filters.js").read_text(encoding="utf-8")

    assert "javascripts/publication-filters.js" in mkdocs
    assert "function initializePublicationFilters(root)" in script
    assert "document$.subscribe(initializePublicationFilters)" in script
    assert "DOMContentLoaded" in script


def test_publications_css_prioritizes_content_and_wraps_tags():
    css = Path("docs/stylesheets/publications.css").read_text(encoding="utf-8")

    assert ".pub-entry {" in css
    assert "grid-template-columns" in css
    assert "flex-wrap: wrap;" in css
    assert "@media (max-width: 900px)" in css
    assert ".pub-filters" in css
    assert ".pub-filter-chip" in css
    assert ".pub-filter-chip.is-active" in css
    assert "[hidden]" in css or ".is-hidden" in css
    assert "width: 300px;" not in css




def test_merged_bib_uses_canonical_venue_names():
    bib = Path("data/publications/merged.bib").read_text(encoding="utf-8")

    assert "SIGCOMM (Best Paper)" not in bib
    assert "ICMR (Best Paper)" not in bib
    assert "SIGIR 2020" not in bib
    assert "SIGMOD Conference 2020" not in bib
    assert "IEEE Transactions on Data and Knowledge Engineering" not in bib
    assert "journal      = {IEEE Transactions on Knowledge and Data Engineering}" in bib
    assert "Computers and Chemical Engineering" not in bib
    assert "Proceedings of the VLDB Endowment" in bib
    assert "ACM Transactions on the Web" in bib
    assert "IEEE Transactions on Knowledge and Data Engineering" in bib
    assert "Computers & Chemical Engineering" in bib


    cache_path = Path("data/publications/publications.cache.json")
    report_path = Path("data/publications/publications.report.json")
    subprocess.run(
        [
            "python3",
            "tools/publications/build_publications.py",
            "--cache",
            str(cache_path),
            "--report",
            str(report_path),
        ],
        check=True,
    )
    subprocess.run(["mkdocs", "build"], check=True)
