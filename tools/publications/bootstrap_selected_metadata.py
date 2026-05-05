from __future__ import annotations

import argparse
from pathlib import Path

from publications_lib import (
    DEFAULT_MERGED_BIB,
    DEFAULT_OVERRIDES,
    DEFAULT_SELECTED_PAGE,
    bootstrap_overrides_from_selected_page,
    load_bib_entries,
    load_json,
    parse_selected_publications_page,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap selected-publication metadata from the current selected page.")
    parser.add_argument("--bib", type=Path, default=DEFAULT_MERGED_BIB)
    parser.add_argument("--selected-page", type=Path, default=DEFAULT_SELECTED_PAGE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OVERRIDES)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bib_entries = load_bib_entries(args.bib)
    selected_entries = parse_selected_publications_page(args.selected_page)
    existing_overrides = load_json(args.output, {})
    overrides, unmatched = bootstrap_overrides_from_selected_page(bib_entries, selected_entries, existing_overrides)
    write_json(args.output, overrides)
    print(f"Bootstrapped {sum(1 for payload in overrides.values() if payload.get('selected'))} selected entries into {args.output}.")
    if unmatched:
        print(f"Warning: {len(unmatched)} selected-page entries could not be matched.")


if __name__ == "__main__":
    main()
