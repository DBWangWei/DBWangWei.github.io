from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from html import escape, unescape
from pathlib import Path
from typing import Any

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter


ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs"
DATA_DIR = ROOT / "data" / "publications"
DEFAULT_MERGED_BIB = DATA_DIR / "merged.bib"
DEFAULT_OVERRIDES = DATA_DIR / "overrides.json"
DEFAULT_CACHE = DATA_DIR / "publications.cache.json"
DEFAULT_REPORT = DATA_DIR / "publications.report.json"
DEFAULT_SELECTED_PAGE = ROOT / "docs" / "intro" / "publications_selected.md"
DEFAULT_ALL_PAGE = ROOT / "docs" / "intro" / "publications.md"
DEFAULT_EXTERNAL_BIB = Path("/Users/weiwang/weiw/Research/=Grant.Proposal/my-bib/WeiWang.bib")

AREA_TOOLTIPS = {
    "AI4S": "AI for Science",
    "ANN": "Approximate Nearest Neighbor",
    "AdvML": "Adversarial ML",
    "App": "Applications",
    "DB": "Database Systems",
    "DL": "Deep Learning",
    "Graph": "Graph",
    "High-Dim": "High-dimensional Data",
    "LLM": "Large Language Models",
    "PDE": "Partial Differential Equations",
    "Theory": "Theory",
    "XAI": "Explainable AI",
}

AREA_ALIASES = {
    "APP": "App",
    "APPLICATION": "App",
    "APPLICATIONS": "App",
    "ADVML": "AdvML",
    "AI4S": "AI4S",
    "ANN": "ANN",
    "DB": "DB",
    "DEEPLEARNING": "DL",
    "DL": "DL",
    "GRAPH": "Graph",
    "HIGHDIM": "High-Dim",
    "HIGHDIM": "High-Dim",
    "LLM": "LLM",
    "PDE": "PDE",
    "THEORY": "Theory",
    "XAI": "XAI",
}

AREA_RULES = [
    ("LLM", [r"large language model", r"\bllm\b", r"fine-tun", r"preference", r"dpo", r"detox", r"dialogue"]),
    ("AI4S", [r"\bpde\b", r"operator", r"physics", r"scientific", r"structural dynamics", r"tcad", r"energy", r"cad drawing"]),
    ("PDE", [r"\bpde\b", r"operator"]),
    ("ANN", [r"approximate nearest neighbor", r"\baknn\b", r"nearest neighbor", r"metric nearness", r"quantization", r"projection"]),
    ("High-Dim", [r"high[- ]dim", r"nearest neighbor", r"metric nearness", r"approximate nearest neighbor"]),
    ("DB", [r"\bvldb\b", r"\bicde\b", r"\bsigmod\b", r"\btkde\b", r"entity resolution", r"query", r"index", r"road network", r"database"]),
    ("Graph", [r"graph", r"road network", r"bipartite", r"shortest distance", r"signed graph"]),
    ("XAI", [r"shapley", r"interpretable", r"explain", r"calibration"]),
    ("AdvML", [r"adversarial", r"robust"]),
    ("Theory", [r"theory", r"tropical", r"proof", r"metric nearness"]),
    ("DL", [r"diffusion", r"neural", r"transformer", r"distillation", r"speech synthesis", r"feature learning"]),
    ("App", [r"driver fatigue", r"appliance", r"restoration", r"vehicle", r"energy", r"application"]),
]


@dataclass
class DuplicateReport:
    kept_id: str
    dropped_id: str
    reason: str
    fingerprint: str


class PublicationBuildError(ValueError):
    pass


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_bib_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        database = bibtexparser.load(handle)
    return [dict(entry) for entry in database.entries]


def write_bib_entries(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    database = BibDatabase()
    database.entries = sorted(
        [dict(entry) for entry in entries],
        key=lambda entry: (-safe_int(entry.get("year")), entry.get("ID", "")),
    )
    writer = BibTexWriter()
    writer.indent = "  "
    writer.order_entries_by = None
    writer.align_values = True
    path.write_text(writer.write(database), encoding="utf-8")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def duplicate_reports_to_dicts(duplicates: list[DuplicateReport]) -> list[dict[str, Any]]:
    return [duplicate.__dict__ for duplicate in duplicates]


def safe_int(value: Any, default: int = 0) -> int:
    match = re.search(r"\d{4}", str(value or ""))
    return int(match.group(0)) if match else default


def strip_braces(text: str) -> str:
    text = text or ""
    text = re.sub(r"[{}]", "", text)
    return normalize_whitespace(text)


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text or "")).strip()


def normalize_title(text: str) -> str:
    text = strip_braces(text).casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return normalize_whitespace(text)


def clean_html_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return normalize_whitespace(text)


def normalize_area_tag(tag: str) -> str:
    raw = normalize_whitespace(tag)
    key = re.sub(r"[^A-Za-z0-9]+", "", raw).upper()
    return AREA_ALIASES.get(key, raw)


def split_authors(author_field: str) -> list[str]:
    authors = []
    for raw_name in (author_field or "").split(" and "):
        name = normalize_whitespace(raw_name)
        if not name:
            continue
        if "," in name:
            parts = [part.strip() for part in name.split(",") if part.strip()]
            if len(parts) >= 2:
                name = f"{parts[1]} {parts[0]}"
        authors.append(name)
    return authors


def format_authors(authors: list[str]) -> str:
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]} and {authors[1]}"
    return ", ".join(authors[:-1]) + f", and {authors[-1]}"


def first_author_surname(author_field: str) -> str:
    authors = split_authors(author_field)
    if not authors:
        return "unknown"
    return normalize_title(authors[0].split()[-1])


def fingerprint_for_entry(entry: dict[str, Any]) -> str:
    return "::".join(
        [
            normalize_title(entry.get("title", "")),
            str(safe_int(entry.get("year"))),
            first_author_surname(entry.get("author", "")),
        ]
    )


def venue_for_entry(entry: dict[str, Any]) -> str:
    return strip_braces(entry.get("booktitle") or entry.get("journal") or entry.get("publisher") or "")


def choose_canonical_url(entry: dict[str, Any], override: dict[str, Any]) -> str | None:
    if override.get("url"):
        return override["url"]
    if entry.get("url"):
        return normalize_whitespace(str(entry["url"]))
    doi = normalize_whitespace(str(entry.get("doi", "")))
    if doi:
        return f"https://doi.org/{doi}"
    return None


def infer_areas(title: str, venue: str) -> list[str]:
    haystack = f"{title} {venue}".casefold()
    areas: list[str] = []
    for area, patterns in AREA_RULES:
        if any(re.search(pattern, haystack) for pattern in patterns):
            areas.append(area)
        if len(areas) == 3:
            break
    if not areas:
        if any(token in venue.casefold() for token in ["vldb", "icde", "sigmod", "tkde"]):
            areas.append("DB")
        else:
            areas.append("App")
    unique: list[str] = []
    for area in areas:
        if area not in unique:
            unique.append(area)
    return unique[:3]


def dedupe_entries(entries: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[DuplicateReport]]:
    kept_by_id: dict[str, dict[str, Any]] = {}
    kept_by_fingerprint: dict[str, dict[str, Any]] = {}
    duplicates: list[DuplicateReport] = []
    ordered: list[dict[str, Any]] = []

    for entry in entries:
        key = entry.get("ID")
        if not key:
            raise PublicationBuildError("BibTeX entry is missing ID")
        fingerprint = fingerprint_for_entry(entry)
        if key in kept_by_id:
            duplicates.append(DuplicateReport(key, key, "duplicate_key", fingerprint))
            kept_by_id[key] = entry
            continue
        if fingerprint in kept_by_fingerprint:
            kept = kept_by_fingerprint[fingerprint]
            duplicates.append(DuplicateReport(kept["ID"], key, "duplicate_fingerprint", fingerprint))
            continue
        kept_by_id[key] = entry
        kept_by_fingerprint[fingerprint] = entry
        ordered.append(entry)
    return ordered, duplicates


def merge_bib_entries(existing: list[dict[str, Any]], incoming: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[DuplicateReport]]:
    merged_by_id = {entry["ID"]: dict(entry) for entry in existing if entry.get("ID")}
    existing_fingerprints = {fingerprint_for_entry(entry): entry["ID"] for entry in merged_by_id.values()}
    duplicates: list[DuplicateReport] = []

    for entry in incoming:
        key = entry.get("ID")
        if not key:
            continue
        fingerprint = fingerprint_for_entry(entry)
        if key in merged_by_id:
            merged_by_id[key] = dict(entry)
            existing_fingerprints[fingerprint] = key
            continue
        if fingerprint in existing_fingerprints:
            duplicates.append(DuplicateReport(existing_fingerprints[fingerprint], key, "existing_fingerprint", fingerprint))
            continue
        merged_by_id[key] = dict(entry)
        existing_fingerprints[fingerprint] = key

    merged_entries = sorted(
        merged_by_id.values(),
        key=lambda entry: (-safe_int(entry.get("year")), entry.get("ID", "")),
    )
    return merged_entries, duplicates


def parse_selected_publications_page(path: Path) -> list[dict[str, Any]]:
    content = read_text(path)
    starts = [match.start() for match in re.finditer(r'<div class="pub-entry">', content)]
    entries: list[dict[str, Any]] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(content)
        segment = content[start:end]
        segment = segment.split("</li>", 1)[0]
        title_match = re.search(r'<span class="pub-title">(.*?)</span>', segment, re.S)
        if not title_match:
            continue
        title = clean_html_text(title_match.group(1))
        year_match = re.search(r',\s*(\d{4})(?:\D|$)', segment)
        year = int(year_match.group(1)) if year_match else None
        tags = [clean_html_text(tag) for tag in re.findall(r'class="pub-tag"[^>]*>(.*?)</span>', segment, re.S)]
        note_match = re.search(r'<div class="pub-comment">(.*?)</div>', segment, re.S)
        note = clean_html_text(note_match.group(1)) if note_match else None
        entries.append({
            "title": title,
            "year": year,
            "areas": [normalize_area_tag(tag) for tag in tags if tag],
            "note": note,
        })
    return entries


def bootstrap_overrides_from_selected_page(
    bib_entries: list[dict[str, Any]],
    selected_entries: list[dict[str, Any]],
    existing_overrides: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    existing_overrides = dict(existing_overrides or {})
    bib_by_title_year: dict[tuple[str, int], dict[str, Any]] = {}
    bib_by_title: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in bib_entries:
        normalized_title = normalize_title(entry.get("title", ""))
        year = safe_int(entry.get("year"))
        bib_by_title_year[(normalized_title, year)] = entry
        bib_by_title[normalized_title].append(entry)

    unmatched: list[dict[str, Any]] = []
    for selected in selected_entries:
        normalized_title = normalize_title(selected.get("title", ""))
        year = selected.get("year") or 0
        bib_entry = bib_by_title_year.get((normalized_title, year))
        if bib_entry is None and len(bib_by_title.get(normalized_title, [])) == 1:
            bib_entry = bib_by_title[normalized_title][0]
        if bib_entry is None:
            unmatched.append(selected)
            continue
        key = bib_entry["ID"]
        payload = dict(existing_overrides.get(key, {}))
        payload["selected"] = True
        if selected.get("areas"):
            payload["areas"] = selected["areas"]
        if selected.get("note"):
            payload["note"] = selected["note"]
        existing_overrides[key] = payload

    return dict(sorted(existing_overrides.items())), unmatched


def build_record(entry: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    title = strip_braces(str(entry.get("title", "")))
    authors = split_authors(str(entry.get("author", "")))
    venue = venue_for_entry(entry)
    override_areas = [normalize_area_tag(area) for area in override.get("areas", []) if normalize_whitespace(area)]
    inferred_areas = infer_areas(title, venue)
    areas = override_areas or inferred_areas
    provenance = {
        "areas": "manual" if override_areas else "inferred",
        "selected": "manual" if "selected" in override else "default",
        "url": "manual" if override.get("url") else ("bib" if entry.get("url") or entry.get("doi") else "missing"),
        "pdf": "manual" if override.get("pdf") else "missing",
    }
    record = {
        "id": entry["ID"],
        "entry_type": entry.get("ENTRYTYPE", "misc"),
        "title": title,
        "authors": authors,
        "authors_display": format_authors(authors),
        "venue": venue,
        "year": safe_int(entry.get("year")),
        "selected": bool(override.get("selected", False)),
        "areas": areas,
        "pdf": override.get("pdf") or None,
        "url": choose_canonical_url(entry, override),
        "note": override.get("note") or override.get("award") or None,
        "award": override.get("award") or None,
        "provenance": provenance,
        "fingerprint": fingerprint_for_entry(entry),
        "sort_key": [safe_int(entry.get("year")), normalize_title(title), entry["ID"]],
        "source": "merged.bib",
    }
    if override.get("display"):
        for key, value in override["display"].items():
            record[key] = value
    return record


def sort_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(records, key=lambda record: (-record["year"], normalize_title(record["title"]), record["id"]))


def local_pdf_exists(pdf: str | None) -> bool:
    if not pdf or re.match(r"https?://", pdf):
        return True
    return (ROOT / pdf).exists()


def pdf_href_for_output(pdf: str, output_page: Path) -> str:
    if re.match(r"https?://", pdf):
        return pdf
    try:
        relative_output = output_page.relative_to(DOCS_DIR)
    except ValueError:
        relative_output = Path("intro") / output_page.name
    root_prefix = "../" * (len(relative_output.parent.parts) + 1)
    if pdf.startswith("docs/"):
        return root_prefix + pdf.removeprefix("docs/")
    return root_prefix + pdf.lstrip("/")


def render_record(record: dict[str, Any], output_page: Path) -> str:
    links: list[str] = []
    if record.get("pdf"):
        links.append(f'<a class="pub-link" href="{escape(pdf_href_for_output(record["pdf"], output_page), quote=True)}">PDF</a>')
    if record.get("url"):
        links.append(f'<a class="pub-link" href="{escape(str(record["url"]), quote=True)}">Link</a>')
    links_html = f' <span class="pub-links">{" ".join(links)}</span>' if links else ""
    note_html = f' <div class="pub-comment">{escape(str(record["note"]))}</div>' if record.get("note") else ""
    tags_html = " ".join(
        f'<span class="pub-tag" data-tooltip="{escape(AREA_TOOLTIPS.get(area, area), quote=True)}">{escape(area)}</span>'
        for area in record.get("areas", [])
    )
    return "\n".join(
        [
            "<li>",
            '  <div class="pub-entry">',
            f'    <div class="pub-content"><span class="pub-title">{escape(record["title"])}</span>, <span class="pub-authors">{escape(record["authors_display"])}</span>. <span class="pub-venue">{escape(record["venue"])}</span>, {record["year"]}.{links_html}{note_html}</div>',
            f'    <div class="pub-tags">{tags_html}</div>',
            "  </div>",
            "</li>",
        ]
    )


def render_publications_page(records: list[dict[str, Any]], heading: str, output_page: Path) -> str:
    parts = [
        "---",
        "tags:",
        "  - research",
        "---",
        "",
        '<link rel="stylesheet" href="../../assets/stylesheets/publications.css">',
        "",
        f"# {heading}",
        "",
        "<ul>",
        "",
    ]
    current_year: int | None = None
    for record in sort_records(records):
        if record["year"] != current_year:
            current_year = record["year"]
            parts.extend([f'<h2 class="year-separator">{current_year}</h2>', ""])
        parts.extend([render_record(record, output_page), ""])
    parts.append("</ul>")
    return "\n".join(parts).rstrip() + "\n"
