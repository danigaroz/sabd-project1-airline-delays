# Project Slides — Beamer presentation

15-minute oral defense for SABD 2025/26 Project 1.

## How to compile (Overleaf — same flow as the report)

1. Build a ZIP from the project root:

```bash
cd ~/sabd_project1
zip -r overleaf_slides.zip slides/main.tex plots/
```

2. Go to https://www.overleaf.com → **New Project → Upload Project**.
   Drag-and-drop `overleaf_slides.zip`.
3. Open `main.tex` and click **Recompile**.

> Path note: `main.tex` references the plots as `../plots/...`. If
> Overleaf does not resolve the relative path, move the four PNGs into
> the same directory as `main.tex` and replace `../plots/` with `./` in
> the `\includegraphics` lines.

## Speaker notes

Every slide has a `\note{...}` block with what to say.
By default the notes are hidden. To render them on a second screen
during the presentation (Beamer presenter mode), uncomment this line
near the top of `main.tex`:

```latex
\setbeameroption{show notes on second screen=right}
```

You can also print a notes-only PDF for studying with:

```latex
\setbeameroption{show only notes}
```

## Slide map (15 minutes ≈ 13 slides)

| # | Slide                                  | Time   |
|---|----------------------------------------|--------|
| 1 | Title                                  | 0:30   |
| 2 | Outline                                | 0:30   |
| 3 | Project goal                           | 1:00   |
| 4 | Dataset overview                       | 1:00   |
| 5 | System architecture (diagram)          | 1:30   |
| 6 | Code organization                      | 1:00   |
| 7 | Query 1 — implementation + first plot  | 1:30   |
| 8 | Query 1 — both plots + observations    | 1:00   |
| 9 | Query 2 — implementation + ranking     | 1:30   |
| 10 | Query 2 — cause breakdown             | 1:00   |
| 11 | 4 key implementation decisions        | 1:30   |
| 12 | Benchmark methodology                 | 1:00   |
| 13 | Results table (local vs HDFS)         | 1:00   |
| 14 | Observations                          | 1:00   |
| 15 | Conclusions                           | 0:30   |
| 16 | Thank you / Questions                 | --     |
