# Documentation index

Files are grouped by purpose. Version numbers in file names match the roadmap (`ROADMAP.md`). Figures and tables stay in `figures/<version>/`; the analysis scripts in `ns-3.29/scratch/linear-mesh/` write there by default.

| Folder | What it holds |
|---|---|
| `planning/` | Project spec and the per-version roadmap with completion criteria. Read first. |
| `design/` | Multi-AP design contract and the optional central-critic design and prototype. |
| `adr/` | Architecture decision records (ADR-0001 to ADR-0004, plus the template). |
| `results/` | One write-up per experiment version: baseline, validation, benchmarks, scaling, robustness, final results, v3.0.0. |
| `reports/` | Final deliverables: technical report, presentation notes, final audit. |
| `reference/` | Supporting material: OSCAR paper metrics, CW literature survey, reproducibility guide, pre-v0.1.0 audits. |
| `figures/` | Generated tables (`tables.md`), CSVs and plots per benchmark version. |

## planning/
- `project_description.md`: full spec and terminology.
- `detailed_roadmap.md`: per-version completion criteria.

## design/
- `multi-ap-design-v0.2.0.md`: multi-AP design specification (v0.2.0).
- `central-critic-v1.7.0.md`: central-critic design (spec only).
- `central-critic-v1.8.0.md`: central-critic prototype.

## adr/
- `0001-record-architecture-decisions.md`
- `0002-multi-ap-v0-2-0-defaults.md`
- `0003-central-critic-ctde.md`: optional central critic (accepted as optional, negative result).
- `0004-relaxed-isolation.md`: relaxed per-AP isolation used by `--mode shared`.
- `adr-template.md`

## results/ (in version order)
- `baseline-v0.1.0.md`: single-AP baseline freeze.
- `validation-v0.9.0.md`, `core-v1.0.0.md`: two-AP validation and core milestone.
- `benchmark-v1.1.0.md`: first benchmarks (BEB, global, independent).
- `scaling-v1.2.0.md` to `scaling-v1.5.0.md`: 4, 6, 8, 10 APs. `scaling-v1.6.0.md`: scaling analysis 2 to 10 APs.
- `central-eval-v1.9.0.md`: central-critic evaluation and follow-ups.
- `robustness-v2.0.0.md`: robustness experiments.
- `final-results-v2.2.0.md`: final result set (81 runs, n=3).
- `improvement-v3.0.0.md`: attempt to beat Global-CW OSCAR (neutral result).

## reports/
- `technical-report-v2.3.0.md`: full write-up.
- `presentation-v2.4.0.md`: deck notes and demo script.
- `final-audit-v2.5.0.md`: 26-item final audit.

## reference/
- `oscar-baseline-metrics.md`: published OSCAR numbers and how they map to this project.
- `cw-literature-survey-2026-10-29.html`: literature survey of contention window optimization (70 entries, 1994 to 2026: BEB, analytical, heuristic, control, game theory, ML, DRL, MARL, LLM, 802.11be/bn), with relevance to this project. Open in a browser.
- `reproducibility-v2.1.0.md`: how to reproduce runs, dependencies.
- `pre_v0.1.0_audit/`: forensic audit of the inherited OSCAR code and the next-actions results.
