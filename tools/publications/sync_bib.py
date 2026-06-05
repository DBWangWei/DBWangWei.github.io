from __future__ import annotations

import argparse
from pathlib import Path

from publications_lib import (
    DEFAULT_EXTERNAL_BIB,
    DEFAULT_MERGED_BIB,
    DEFAULT_REPORT,
    duplicate_reports_to_dicts,
    load_bib_entries,
    load_json,
    merge_bib_entries,
    write_bib_entries,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync external BibTeX into the repo-local merged bibliography.")
    parser.add_argument("--source", type=Path, default=DEFAULT_EXTERNAL_BIB)
    parser.add_argument("--merged", type=Path, default=DEFAULT_MERGED_BIB)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    merged_entries = load_bib_entries(args.merged)
    source_entries = load_bib_entries(args.source)
    merged, duplicates = merge_bib_entries(merged_entries, source_entries)
    write_bib_entries(args.merged, merged)

    report_payload = load_json(args.report, {}) if args.report.exists() else {}
    report_payload["sync_duplicates"] = duplicate_reports_to_dicts(duplicates)
    write_json(args.report, report_payload)

    print(f"Synced {len(source_entries)} source entries into {args.merged}.")
    if duplicates:
        print(f"Skipped {len(duplicates)} duplicate fingerprint entries.")


if __name__ == "__main__":
    main()
