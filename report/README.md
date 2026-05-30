# Project Report — Compile on Overleaf

The report lives in `main.tex` and is written for the IEEEtran conference
template (the official IEEE proceedings format).

## How to compile (Overleaf — recommended)

1. Go to https://www.overleaf.com and sign in (free account is enough).
2. **New Project → Upload Project**. Drag-and-drop a ZIP that contains:
   - `main.tex`
   - the `plots/` directory (so the figures resolve at compile time)
3. Once uploaded, open `main.tex` and click **Recompile**. The PDF
   appears on the right.

To build the ZIP from the project root:

```bash
cd ~/sabd_project1
zip -r overleaf_upload.zip report/main.tex plots/
```

Then upload `overleaf_upload.zip` to Overleaf.

> Note about figure paths: `main.tex` references the plots as
> `../plots/q1_avg_dep_delay.png` etc. If Overleaf does not resolve the
> relative path, simply move the four PNGs into the same directory as
> `main.tex` and replace `../plots/` with `./` in the `\includegraphics`
> lines.

## How to compile locally (optional)

```bash
sudo apt install -y texlive-latex-recommended texlive-fonts-recommended \
                    texlive-latex-extra texlive-pictures
cd report
pdflatex main.tex
pdflatex main.tex   # 2nd pass for cross-references
```

The output is `main.pdf`.
