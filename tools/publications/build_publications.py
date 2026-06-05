from __future__ import annotations

import argparse
from pathlib import Path

from publications_lib import (
    DEFAULT_ALL_PAGE,
    DEFAULT_CACHE,
    DEFAULT_MERGED_BIB,
    DEFAULT_OVERRIDES,
    DEFAULT_REPORT,
    DEFAULT_SELECTED_PAGE,
    build_record,
    dedupe_entries,
    load_bib_entries,
    load_json,
    local_pdf_exists,
    render_publications_page,
    sort_records,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build publication cache, report, and Markdown pages from merged BibTeX + overrides.")
    parser.add_argument("--bib", type=Path, default=DEFAULT_MERGED_BIB)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--selected-page", type=Path, default=DEFAULT_SELECTED_PAGE)
    parser.add_argument("--all-page", type=Path, default=DEFAULT_ALL_PAGE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    overrides = load_json(args.overrides, {})
    bib_entries = load_bib_entries(args.bib)
    deduped_entries, duplicates = dedupe_entries(bib_entries)
    records = sort_records([build_record(entry, overrides.get(entry["ID"], {})) for entry in deduped_entries])
    selected_records = [record for record in records if record["selected"]]
    missing_local_pdfs = [record["pdf"] for record in records if record.get("pdf") and not local_pdf_exists(record["pdf"])]
    inferred_area_ids = [record["id"] for record in records if record["provenance"]["areas"] == "inferred"]

    cache_payload = {
        "records": records,
        "summary": {
            "all_count": len(records),
            "selected_count": len(selected_records),
            "year_range": [records[-1]["year"], records[0]["year"]] if records else [],
        },
    }
    report_payload = load_json(args.report, {}) if args.report.exists() else {}
    report_payload.update(
        {
            "duplicates": [duplicate.__dict__ for duplicate in duplicates],
            "missing_local_pdfs": missing_local_pdfs,
            "inferred_areas": inferred_area_ids,
            "selected_count": len(selected_records),
            "all_count": len(records),
        }
    )

    write_json(args.cache, cache_payload)
    write_json(args.report, report_payload)
    args.selected_page.write_text(render_publications_page(selected_records, "Selected Publications", args.selected_page), encoding="utf-8")
    args.all_page.write_text(render_publications_page(records, "All Publications", args.all_page), encoding="utf-8")
    print(f"Built {len(records)} publication records.")


if __name__ == "__main__":
    main()
