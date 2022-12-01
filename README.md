BXjakyureki Package
===================

LaTeX: Support for Japanese old lunisolar calendar (kyūreki; 旧暦)

## System requiremnts

  * TeX format: LaTeX
  * TeX engine: e-pTeX, e-upTeX, LuaTeX, XeTeX or pdfTeX
     - Of course, you need a Japanese typesetting package (like LuaTeX-ja, zxjatype or CJKutf8), if you use LuaLaTeX, XeLaTeX or pdfLaTeX

## Usage

This package provides following LaTeX2e commands:

```latex
\jakyureki{<year>}{<month>}{<day>}
```

## Installation

Strip package file.

```
$ pdftex bxjakyureki.ins
```

Install files.

  * `*.sty`/`*.def` → $TEXMF/tex/latex/bxjakyureki/
  * `*.dtx`/`*.ins` → $TEXMF/source/latex/bxjakyureki/
  * `*.pdf` → $TEXMF/doc/latex/bxjakyureki/

### Building in development repository

Install to TEXMFHOME.

```
l3build install --full
```

Typeset documentation.

```
l3build doc
```

Run tests.

```
l3build check
```

## License

This package is distributed under [the MIT License](LICENSE).

---
Yukimasa Morimi ([h20y6m](https://github.com/h20y6m))
