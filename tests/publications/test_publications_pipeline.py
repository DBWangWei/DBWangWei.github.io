import json
import subprocess
import textwrap
from pathlib import Path


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
    return path


def test_bootstrap_selected_metadata_matches_current_selected_entries(tmp_path):
    bib_path = write_text(
        tmp_path / "merged.bib",
        """
        @InProceedings{paper2026,
          title = {Elastic Index Selection for Label-Hybrid {AKNN} Search},
          author = {Mingyu Yang and Wei Wang},
          booktitle = {VLDB},
          year = {2026}
        }

        @InProceedings{paper2025,
          title = {{PUER}: Boosting Few-shot Positive-Unlabeled Entity Resolution with Reinforcement Learning},
          author = {Yaoshu Wang and Wei Wang},
          booktitle = {EMNLP Findings},
          year = {2025}
        }

        @InProceedings{paperLigature,
          title = {Robustness Feature Adapter for Efficient Adversarial Training},
          author = {Quanwei Wu and Wei Wang},
          booktitle = {ECAI},
          year = {2025}
        }
        """,
    )
    selected_path = write_text(
        tmp_path / "publications_selected.md",
        """
        ---
        tags:
          - research
        ---

        <ul>
        <h2 class="year-separator">2026</h2>
        <li>
          <div class="pub-entry">
            <div class="pub-content"><span class="pub-title">Elastic Index Selection for Label-Hybrid AKNN Search</span>, <span class="pub-authors">Mingyu Yang and Wei Wang</span>. <span class="pub-venue">VLDB</span>, 2026</div>
            <div class="pub-tags">
              <span class="pub-tag" data-tooltip="Approximate Nearest Neighbor">ANN</span>
              <span class="pub-tag" data-tooltip="High-dimensional Data">High-Dim</span>
            </div>
          </div>
        </li>
        <h2 class="year-separator">2025</h2>
        <li>
          <div class="pub-entry">
            <div class="pub-content"><span class="pub-title">PUER: Boosting few-shot positive-unlabeled entity resolution with reinforcement learning</span>, <span class="pub-authors">Yaoshu Wang and Wei Wang</span>. <span class="pub-venue">EMNLP Findings</span>, 2025<div class="pub-comment">Best Student Paper</div></div>
            <div class="pub-tags">
              <span class="pub-tag" data-tooltip="Database">DB</span>
            </div>
          </div>
        </li>
        <li>
          <div class="pub-entry">
            <div class="pub-content"><span class="pub-title">Robustness feature adapter for eﬃcient adversarial training</span>, <span class="pub-authors">Quanwei Wu and Wei Wang</span>. <span class="pub-venue">ECAI</span>, 2025</div>
            <div class="pub-tags">
              <span class="pub-tag" data-tooltip="Application">APP</span>
            </div>
          </div>
        </li>
        </ul>
        """,
    )
    output_path = tmp_path / "overrides.json"

    subprocess.run(
        [
            "python3",
            "tools/publications/bootstrap_selected_metadata.py",
            "--bib",
            str(bib_path),
            "--selected-page",
            str(selected_path),
            "--output",
            str(output_path),
        ],
        check=True,
    )

    overrides = json.loads(output_path.read_text(encoding="utf-8"))
    assert overrides["paper2026"]["selected"] is True
    assert overrides["paper2026"]["areas"] == ["ANN", "High-Dim"]
    assert overrides["paper2025"]["selected"] is True
    assert overrides["paper2025"]["areas"] == ["DB"]
    assert overrides["paper2025"]["note"] == "Best Student Paper"
    assert overrides["paperLigature"]["selected"] is True
    assert overrides["paperLigature"]["areas"] == ["App"]


def test_build_publications_generates_cache_report_and_pages(tmp_path):
    bib_path = write_text(
        tmp_path / "merged.bib",
        """
        @InProceedings{selected2026,
          title = {Elastic Index Selection for Label-Hybrid {AKNN} Search},
          author = {Mingyu Yang and Wei Wang},
          booktitle = {VLDB},
          year = {2026},
          url = {https://example.com/landing}
        }

        @InProceedings{llm2025,
          title = {Detoxifying Large Language Models via the Diversity of Toxic Samples},
          author = {Ying Zhao and Wei Wang},
          booktitle = {EMNLP},
          year = {2025}
        }

        @InProceedings{dupA,
          title = {Shared Duplicate Title},
          author = {Alice Smith and Wei Wang},
          booktitle = {KDD},
          year = {2024}
        }

        @InProceedings{dupB,
          title = {Shared Duplicate Title},
          author = {Alice Smith and Wei Wang},
          booktitle = {KDD},
          year = {2024}
        }
        """,
    )
    overrides_path = write_text(
        tmp_path / "overrides.json",
        """
        {
          "selected2026": {
            "selected": true,
            "areas": ["ANN", "High-Dim"],
            "pdf": "docs/papers/2026/elastic-index-selection.pdf",
            "url": "https://example.com/project"
          }
        }
        """,
    )
    cache_path = tmp_path / "publications.cache.json"
    report_path = tmp_path / "publications.report.json"
    selected_page = tmp_path / "publications_selected.md"
    all_page = tmp_path / "publications.md"

    subprocess.run(
        [
            "python3",
            "tools/publications/build_publications.py",
            "--bib",
            str(bib_path),
            "--overrides",
            str(overrides_path),
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
    report = json.loads(report_path.read_text(encoding="utf-8"))
    selected_md = selected_page.read_text(encoding="utf-8")
    all_md = all_page.read_text(encoding="utf-8")

    assert len(cache["records"]) == 3
    assert sum(1 for record in cache["records"] if record["selected"]) == 1
    llm_record = next(record for record in cache["records"] if record["id"] == "llm2025")
    assert llm_record["areas"]
    assert llm_record["provenance"]["areas"] == "inferred"
    assert report["duplicates"]
    assert report["missing_local_pdfs"] == ["docs/papers/2026/elastic-index-selection.pdf"]
    assert selected_md.index("2026") < selected_md.index("Elastic Index Selection")
    assert "../../papers/2026/elastic-index-selection.pdf" in selected_md
    assert "https://example.com/project" in selected_md
    assert all_md.index("2026") < all_md.index("2025") < all_md.index("2024")
    assert "Detoxifying Large Language Models" in all_md
    assert "Shared Duplicate Title" in all_md


def test_build_publications_emits_filter_markup_and_metadata(tmp_path):
    bib_path = write_text(
        tmp_path / "merged.bib",
        """
        @InProceedings{selected2026,
          title = {Elastic Index Selection for Label-Hybrid {AKNN} Search},
          author = {Mingyu Yang and Wei Wang},
          booktitle = {VLDB},
          year = {2026}
        }

        @InProceedings{llm2025,
          title = {Detoxifying Large Language Models via the Diversity of Toxic Samples},
          author = {Ying Zhao and Wei Wang},
          booktitle = {EMNLP},
          year = {2025}
        }
        """,
    )
    overrides_path = write_text(
        tmp_path / "overrides.json",
        """
        {
          "selected2026": {
            "selected": true,
            "areas": ["ANN", "High-Dim"]
          },
          "llm2025": {
            "areas": ["LLM"]
          }
        }
        """,
    )
    selected_page = tmp_path / "publications_selected.md"
    all_page = tmp_path / "publications.md"

    subprocess.run(
        [
            "python3",
            "tools/publications/build_publications.py",
            "--bib",
            str(bib_path),
            "--overrides",
            str(overrides_path),
            "--cache",
            str(tmp_path / "publications.cache.json"),
            "--report",
            str(tmp_path / "publications.report.json"),
            "--selected-page",
            str(selected_page),
            "--all-page",
            str(all_page),
        ],
        check=True,
    )

    selected_md = selected_page.read_text(encoding="utf-8")
    all_md = all_page.read_text(encoding="utf-8")

    assert 'class="pub-filters"' in all_md
    assert 'data-filter-group="tags"' in all_md
    assert 'data-filter-group="venues"' in all_md
    assert 'Clear filters' in all_md
    assert 'data-tags="ann high-dim vldb"' in selected_md
    assert 'data-venue="vldb"' in selected_md
    assert 'data-year="2026"' in selected_md
    assert 'function applyPublicationFilters()' not in all_md
    assert '<script>' not in all_md
    assert 'data-publication-entry="true"' in all_md
    assert 'data-publication-year="2026"' in all_md
    assert 'data-selected-tag' in all_md




def test_build_publications_emits_award_and_venue_family_tags(tmp_path):
    bib_path = write_text(
        tmp_path / "merged.bib",
        """
        @Article{pvldb2024,
          title = {A VLDB Endowment Paper},
          author = {Alice Example and Wei Wang},
          journal = {Proceedings of the VLDB Endowment},
          year = {2024}
        }

        @InProceedings{sigcomm2022,
          title = {A SIGCOMM Award Paper},
          author = {Bob Example and Wei Wang},
          booktitle = {SIGCOMM},
          award = {Best Paper},
          year = {2022}
        }
        """,
    )
    overrides_path = write_text(
        tmp_path / "overrides.json",
        """
        {
          "pvldb2024": {
            "areas": ["DB"]
          },
          "sigcomm2022": {
            "areas": ["Graph"]
          }
        }
        """,
    )
    all_page = tmp_path / "publications.md"

    subprocess.run(
        [
            "python3",
            "tools/publications/build_publications.py",
            "--bib",
            str(bib_path),
            "--overrides",
            str(overrides_path),
            "--cache",
            str(tmp_path / "publications.cache.json"),
            "--report",
            str(tmp_path / "publications.report.json"),
            "--selected-page",
            str(tmp_path / "publications_selected.md"),
            "--all-page",
            str(all_page),
        ],
        check=True,
    )

    all_md = all_page.read_text(encoding="utf-8")

    assert '<span class="pub-venue">Proceedings of the VLDB Endowment</span>' in all_md
    assert '<span class="pub-tag" data-tooltip="VLDB">VLDB</span>' in all_md
    assert '<span class="pub-tag" data-tooltip="Best Paper">Best Paper</span>' in all_md
    assert 'data-tags="db vldb"' in all_md
    assert 'data-tags="graph best-paper"' in all_md
    assert '<div class="pub-comment">Best Paper</div>' in all_md
    bib_path = write_text(
        tmp_path / "merged.bib",
        """
        @InProceedings{paper2026,
          title = {Elastic Index Selection for Label-Hybrid {AKNN} Search},
          author = {Mingyu Yang and Wei Wang},
          booktitle = {VLDB},
          year = {2026}
        }
        """,
    )
    overrides_path = write_text(tmp_path / "overrides.json", "{}")
    report_path = write_text(
        tmp_path / "publications.report.json",
        """
        {
          "sync_duplicates": [
            {
              "kept_id": "localOnly",
              "dropped_id": "differentKeySamePaper",
              "reason": "existing_fingerprint",
              "fingerprint": "local only paper::2023::jones"
            }
          ]
        }
        """,
    )
    cache_path = tmp_path / "publications.cache.json"
    selected_page = tmp_path / "publications_selected.md"
    all_page = tmp_path / "publications.md"

    subprocess.run(
        [
            "python3",
            "tools/publications/build_publications.py",
            "--bib",
            str(bib_path),
            "--overrides",
            str(overrides_path),
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

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["sync_duplicates"][0]["kept_id"] == "localOnly"


def test_sync_bib_records_duplicate_collisions_in_report(tmp_path):
    merged_path = write_text(
        tmp_path / "merged.bib",
        """
        @InProceedings{localOnly,
          title = {Local Only Paper},
          author = {Bob Jones and Wei Wang},
          booktitle = {KDD},
          year = {2023}
        }
        """,
    )
    source_path = write_text(
        tmp_path / "source.bib",
        """
        @InProceedings{differentKeySamePaper,
          title = {Local Only Paper},
          author = {Bob Jones and Wei Wang},
          booktitle = {KDD},
          year = {2023}
        }
        """,
    )
    report_path = tmp_path / "publications.report.json"

    subprocess.run(
        [
            "python3",
            "tools/publications/sync_bib.py",
            "--source",
            str(source_path),
            "--merged",
            str(merged_path),
            "--report",
            str(report_path),
        ],
        check=True,
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["sync_duplicates"]
    assert report["sync_duplicates"][0]["kept_id"] == "localOnly"
    assert report["sync_duplicates"][0]["dropped_id"] == "differentKeySamePaper"


