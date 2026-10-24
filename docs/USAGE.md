# Usage guide

## Which family should I use?

| Need | Family |
| --- | --- |
| Interface, text, branding with soft shapes | **Geist Rounded by Nortics** |
| Same design with the crisp corners of the original | **Geist Sharp by Nortics** |
| Code, terminals, tables with soft shapes | **Geist Rounded Mono by Nortics** |
| Code with crisp corners | **Geist Sharp Mono by Nortics** |

The four families have different names, so they can all be installed at the same time, and together with the original Geist.

## Weights

CSS `font-weight` takes plain numbers, so every weight is addressable, including the intermediate ones.

| `font-weight` | Style | Sans | Mono |
| --- | --- | :-: | :-: |
| 100 | Thin | yes | yes |
| 150 | UltraLight | yes | - |
| 200 | ExtraLight | yes | yes |
| **250** | **SemiLight** | yes | yes |
| 300 | Light | yes | yes |
| 400 | Regular | yes | yes |
| 500 | Medium | yes | yes |
| 600 | SemiBold | yes | yes |
| 700 | Bold | yes | yes |
| 800 | ExtraBold | yes | yes |
| 900 | Black | yes | - |

## Install on the desktop

Use the `.ttf` files in `fonts/<family>/ttf/`.

- **Windows:** select the files, right-click, *Install* (or *Install for all users*).
- **macOS:** double-click a file and press *Install Font*, or drop the files in Font Book.
- **Linux:** copy the files to `~/.local/share/fonts/` and run `fc-cache -f`.

Applications list the fonts by family. Because the weights 150 and 250 are not part of the classic 400/700 style-linking, applications show them as extra styles of the same family (for example *Geist Rounded by Nortics SemiLight*); this is normal.

## Use on the web

Self-host the `.woff2` files and link `web/webfonts.css` (it declares every weight with `font-display: swap`). The paths inside the CSS are relative to the file, so keep the folder layout (`web/` next to `fonts/`), or adjust the `url()` values.

```html
<link rel="stylesheet" href="/nortics-geist/web/webfonts.css">
```

No hosting at hand? The same CSS and fonts can be loaded from the jsDelivr CDN, pinned to a release tag (the font URLs inside the CSS resolve correctly because the folder layout is the same):

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/younner-org/nortics-geist-typeface@v1.100/web/webfonts.css">
```

For production, self-hosting is recommended: it avoids a third-party request and a dependency on an external service.

```css
:root {
  --font-sans: "Geist Rounded by Nortics", system-ui, sans-serif;
  --font-mono: "Geist Rounded Mono by Nortics", ui-monospace, monospace;
}
body   { font-family: var(--font-sans); font-weight: 400; }
h1     { font-weight: 700; letter-spacing: 0; }
.quote { font-weight: 250; }            /* SemiLight */
pre, code { font-family: var(--font-mono); }
```

Tailwind CSS:

```js
// tailwind.config.js
module.exports = {
  theme: { extend: { fontFamily: {
    sans: ['"Geist Rounded by Nortics"', "system-ui", "sans-serif"],
    mono: ['"Geist Rounded Mono by Nortics"', "ui-monospace", "monospace"],
  } } },
};
```

## Ligatures (arrows)

The arrow ligatures are the `liga` feature, which is on by default in browsers, VS Code and most design tools.

| Type | Result |
| --- | --- |
| `->` `-->` `--->` | right arrows, shaft of 1, 2 and 3 hyphens |
| `<-` `<--` `<---` | left arrows |
| `<->` `<-->` `<--->` | double-headed arrows |

Turn them off where you need the literal characters:

```css
code.literal { font-variant-ligatures: none; }
/* or: font-feature-settings: "liga" 0; */
```

In the Mono every ligature occupies exactly as many cells as the characters you typed, so columns stay aligned in code and tables.

## Code editors

VS Code (`settings.json`):

```json
{
  "editor.fontFamily": "'Geist Rounded Mono by Nortics', Consolas, monospace",
  "editor.fontWeight": "400",
  "editor.fontLigatures": true
}
```

Use `"editor.fontLigatures": false` to see the plain characters. Terminals that do not support ligatures simply show the characters one by one.

## OpenType features

Stylistic sets, fractions, case-sensitive forms, tabular figures and the other features of Geist are available through `font-feature-settings` (for example `"ss01" 1`, `"frac" 1`, `"case" 1`, and `"tnum" 1` in the sans; the Mono figures are already tabular). The exact list per family is in [OPENTYPE-FEATURES.md](OPENTYPE-FEATURES.md); not every tag exists in every family.

## Things to know

- The fonts are **unhinted**: on very low-resolution Windows (GDI) rendering the text can look softer than a hinted font. On modern displays and with DirectWrite/CoreText it renders normally.
- There is **no italic** and **no variable font**. Browsers will synthesize an oblique if you ask for `font-style: italic`; avoid it for finished work.
- Language coverage and the glyph set: [GLYPH-COVERAGE.md](GLYPH-COVERAGE.md).
