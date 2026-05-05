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
    assert selected_md.count('<div class="pub-entry">') == cache["summary"]["selected_count"]
    assert all_md.count('<div class="pub-entry">') == cache["summary"]["all_count"]


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


def test_mkdocs_build_succeeds_after_publications_refresh(tmp_path):
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
