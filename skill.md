---
name: readme-to-argument-specs
description: >-
  Convert a linux-system-roles hand-written README.md into a native
  meta/argument_specs.yml (antsibull semantic-markup fields) and generate
  a README.md and a self-contained README.html from it. Use when asked to
  "generate role docs from argument_specs", "convert the README to
  argument_specs", document a role's returned variables, add examples / notes /
  attributes to a role's argument_specs, or fix escaped backticks/links in a
  generated role README.
---

# README.md → meta/argument_specs.yml

Turn a role's hand-written `README.md` into documentation that lives entirely in
`meta/argument_specs.yml` using **native antsibull fields**, then render
`README.md` (and a styled `README.html` preview) from it.

`README.md` is the canonical, superior rendering, so the build deliberately does
**not** emit `README.txt` or `README.rst`. RST is still produced internally as a
build intermediate (antsibull emits it; Sphinx consumes it to build the HTML),
but it is not copied out.

## Core principles

- **Native fields, with one documented exception.** Documentation content lives
  in `meta/argument_specs.yml` native antsibull fields (`short_description`,
  `description`, `author`, `notes`, `attributes`, `options`, `examples`). The
  sole exception is **returned variables**: the native `return:` key is not yet
  accepted by the released ansible-lint role-arg-spec schema, so it lives in a
  separate `meta/set_vars_specs.yml` and is merged back in only at build time
  (see "Returned variables" and "Build pipeline"). This keeps
  `argument_specs.yml` lint-clean with no `schema[role-arg-spec]` skip.
- **Lose no content.** The conversion must preserve every fact from the original
  `README.md` — every variable, default, choice, warning, requirement, caveat,
  and example. Dropping information is a bug, not a simplification. See
  "Preserve content, improve prose" below.
- **Generated artifacts are never hand-edited.** `README.md` and `README.html`
  are build outputs — edit `argument_specs.yml` (or `meta/set_vars_specs.yml`)
  and rebuild. `README.html` is a single self-contained file; no `sphinx_html/`
  tree or `_static/` assets are committed.
- **Custom pieces, all shared verbatim across roles and bundled with this skill:**
  `.build_docs.sh` (orchestration), `.html_to_md.py` (antsibull has no Markdown
  output), `.html_to_singlefile.py` (collapses the Sphinx site into one
  `README.html` and trims fonts), and `.merge_set_vars.py` (merges
  `set_vars_specs.yml` back in as `return:`). Keep machinery minimal.
- **All work is local.** Do not commit or push anything unless the user
  explicitly asks.

## Where content goes (entry point `main`)

| Field | Renders as | Put here |
|---|---|---|
| `short_description` | page subtitle | one-line role summary |
| `description` | **Synopsis** | role summary **and all narrative/operational prose**: providers, requirements, warnings, compatibility, limitations, caveats. One list item = one bullet. |
| `author` | Authors | list of names |
| `notes` | **Notes** | **only low-level, implementation-level details** — why some variables are intentionally not declared, how fact-dependent defaults resolve, and (if the role returns variables) a one-line pointer to `meta/set_vars_specs.yml`. One list item = one bullet. |
| `attributes` | Attributes table | `platform` (with a `platforms:` list), `check_mode`, etc. Every attribute needs a `support:` value. Mirror `meta/main.yml` galaxy_info platforms. |
| `options` | Parameters table | every role variable: `type`, `default`, `choices`, `description`, nested sub-`options`. |
| `examples` | Examples | an `examples: |` literal block of full plays (`name`, `hosts`, `vars`, `roles`). |
| `return:` in `meta/set_vars_specs.yml` | **Return Variables** table | every variable the role sets: `type`, `returned`, `sample`, and `contains` for dicts. Kept out of `argument_specs.yml` (released ansible-lint rejects `return:`); merged in at build time. See "Returned variables". |

**Include a section only when it carries real content.** `short_description`,
`description`, and `options` are effectively always present. `author`, `notes`,
`attributes`, and `examples` are optional — omit the field entirely when there is
nothing genuine to say, rather than emitting an empty or filler section. In
particular, **omit `notes` when the role has no low-level internals or returned
variables** to document; do not pad it with prose that belongs in the Synopsis.

### Synopsis vs Notes vs returned variables

- **Synopsis (`description`)** carries everything a reader needs up front,
  including warnings, compatibility, and limitations.
- **Notes** is reserved for genuinely low-level internals. In `network` there
  are no returned variables, so Notes holds the default-resolution internals
  (why `network_provider` etc. are not declared, why
  `network_ignore_errors`/`network_force_state_change` have no default in
  `defaults/main.yml`).
- **Returned variables** are documented natively as a `return:` mapping (`type`,
  `returned`, `sample`, and `contains` for dicts) that renders as a proper
  "Return Variables" table — NOT as Notes prose. This supersedes the earlier
  `bootloader` approach of listing returns as `• C(var) — ...` Notes bullets.

### Returned variables (the `return:` / `set_vars_specs.yml` split)

The native `return:` key renders a "Return Variables" table, but two tools lag:

- The **released ansible-lint** role-arg-spec schema does not allow `return:`
  (adding it forces a `schema[role-arg-spec]` skip). It *does* allow `notes`
  (confirmed: `ha_cluster` uses `notes` with no skip). The released schema's
  entry-point keys are `attributes, author, description, examples, options,
  seealso, short_description, version_added`.
- The **released antsibull-docs** does not render a role's `return:` key (needs
  the patched fork — see "Build pipeline").

So, to keep `argument_specs.yml` lint-clean by default:

1. Put the returned-variable docs in `meta/set_vars_specs.yml` under a top-level
   `return:` key (exactly the mapping the native `return:` field expects).
2. Add ONE `notes` bullet in `argument_specs.yml` pointing readers at it, e.g.
   *"This role sets variables, for the full list of returned variables see
   'Return Variables' in README.html and README.md, or
   C(meta/set_vars_specs.yml)."*
3. At build time `.merge_set_vars.py` injects that mapping back into a throwaway
   copy of `argument_specs.yml` as `return:` and drops the pointer note, so the
   rendered README shows the real table. The committed files are never modified.

The pointer note is matched/removed by the substring `set_vars_specs.yml`; keep
that filename in the note text. Roles with no returned variables need none of
this — no `set_vars_specs.yml`, no pointer note.

## Preserve content, improve prose

Two goals that must not conflict: keep all the information, and write it better.

**Preserve every fact.** Before converting, inventory the source `README.md`:
list every variable, its type/default/choices, and every warning, requirement,
compatibility note, limitation, caveat, and example. After building, confirm each
item landed somewhere in the generated `README.md` (an option, a Synopsis/Notes
bullet, an attribute, or an example). Nothing from the original may silently
disappear. If something no longer applies, say so explicitly — do not just drop
it. When unsure whether a detail still matters, keep it.

**Improve the wording to technical-documentation standards.** You are rewriting
prose into `argument_specs.yml` fields, so tighten it as you go — same meaning,
clearer delivery:

- **Clear and concise.** Cut filler ("in order to" → "to", "is able to" → "can").
  One idea per sentence. Prefer short sentences over clause-stacked ones.
- **Avoid ambiguity.** Name the exact variable/value/file; avoid vague "it",
  "this", "the above". State who does what to what.
- **Simpler language.** Prefer the active voice ("the role configures X", not "X
  is configured by the role") and simple tenses (present tense for behavior: "the
  role installs", not "the role will have installed"). Avoid "will"/"would" where
  present tense reads cleaner.
- **Consistent terms.** Use one name for one thing throughout (e.g. always
  "profile", not "profile"/"connection"/"config" interchangeably).
- **One sentence per line (source formatting).** Within folded (`>`) description
  scalars, put each sentence on its own source line. Folding rejoins them with
  spaces, so the rendered output is unchanged, but diffs become sentence-granular.
  Long single-sentence lines are fine (the shared `.yamllint.yml` does not enforce
  line length; `ha_cluster` has 280-char lines). This is formatting only — never
  let it change wording or meaning.

Rephrasing to be clearer is expected and encouraged; changing the meaning or
omitting a fact is not. If a rewrite risks altering meaning, keep the original
phrasing.

## Semantic markup (NOT Markdown)

antsibull does **not** treat descriptions as Markdown. Literal backticks and
`[text](url)` pass through and pandoc escapes them (`\``, `\[`, `\]`) — that is
exactly the defect to eliminate. Convert **everything** to macros:

- `L(text,url)` — links. (`[text](url)` → `L(text,url)`)
- `V(value)` — literal values: `true`/`false`, choice values, enum values, IP
  addresses, numbers, MAC addresses, `nm`/`initscripts`, type values, etc.
- `C(code)` — commands, file paths, package names, module names, config tokens,
  **and option/sub-option names used as identifiers**.
- `O(name)` — references to options **defined in this spec**. Only use it for
  **top-level** options (they resolve cleanly). For sibling/nested sub-option
  references use `C()` instead — nested `O()` paths are error-prone and the final
  README strips option cross-refs to plain text anyway (see gotchas).
- `B(text)` — bold (e.g. `B(Warning):`).

The same token is often different macros by context — judge per occurrence
(e.g. `bond` as a type value is `V(bond)`; the `bond` option dictionary is
`C(bond)`; a top-level variable like `network_connections` is
`O(network_connections)`).

**Never use `O()` for a variable that is not declared as an option** (it becomes
an unresolved cross-reference). Undefined/undocumented variables → `C()`.

### Gotchas (all learned the hard way)

- **Parens inside `C()`**: `C(foo())` breaks — the first `)` closes the macro,
  and backslash-escaping (`C(foo\(\))`) leaks backslashes into the output.
  Reword to drop the parens, e.g. "the `C(foo)` function".
- **Possessive `'s` right after a code span**: `C(ethtool)'s` makes pandoc emit a
  wrong-way curly quote. Reword to avoid possessives after a macro.
- **Single-punctuation code spans glued to text**: `C(-)-separated` renders as
  the awkward `` `-`-separated ``. Reword ("hyphen-separated").
- **Option cross-refs are intentionally flattened to plain text** in `README.md`
  by `.html_to_md.py` (a flat README has no anchor targets). So in the final MD,
  `O()` and `C()` look the same except `O()` is bold. This is why `O()` is only
  worth using for defined top-level options.
- **Large lists of undescribed values** (e.g. the ~90 all-boolean `ethtool`
  `features`): don't describe each entry. Point the parent `description` at the
  upstream tool (`ethtool -k <device>`, `man 8 ethtool`) and state they are all
  boolean toggles.

## Build pipeline

The pipeline is: `.merge_set_vars.py` (inject `return:`) → antsibull-docs → RST
(intermediate) → Sphinx (HTML) → `.html_to_singlefile.py` (one self-contained
`README.html`) and `.html_to_md.py` (pandoc → `README.md`). `README.txt` and
`README.rst` are not emitted, and no `sphinx_html/` tree is committed.

- **Patched antsibull-docs.** Rendering a role's `return:` key (the "Return
  Variables" table) is not yet in a released antsibull-docs, so `.build_docs.sh`
  installs the patched fork
  (`antsibull-docs @ git+https://github.com/spetrosi/antsibull-docs@role-return-values`)
  into a dedicated venv that is created once and reused (default
  `~/.cache/lsr-antsibull-docs`, override with `ANTSIBULL_RV_VENV`; delete it to
  refresh). First run needs network; later runs are offline. `sphinx` goes into
  the same venv. Drop this once role `return:` support ships upstream.
- **Returned-variables merge.** `.build_docs.sh` mirrors the role into a temp
  collection with symlinks EXCEPT `meta/argument_specs.yml`, which
  `.merge_set_vars.py` regenerates with `set_vars_specs.yml`'s `return:` merged
  in and the pointer note dropped. The committed files are never touched.
- **Single-file README.html + font trimming live in `.html_to_singlefile.py`.**
  It inlines CSS/images as `data:` URIs, drops JS, and hides the docsite chrome,
  producing one dependency-free `README.html`. With `--standalone` it also
  physically removes the Ansible "beyond RTD" top bar (the `.DocSite-globalNav`
  Blog/forum/Documentation links and the `.DocSite-nav` logo+title block, incl.
  its inlined logo PNG), hides the admonition icon
  (`.rst-content .admonition-title:before`, otherwise a broken glyph once fonts
  are dropped), and hides the breadcrumb separator `<hr>` (`.wy-breadcrumbs + hr`)
  left dangling once the breadcrumbs are hidden. The RTD theme bundles Lato +
  Roboto Slab text fonts and FontAwesome icons in several formats (~2MB). Font
  handling (previously a `find -delete` step in `.build_docs.sh`) is controlled
  by the `KEEP_FONTS` constant and the `--drop-fonts` flag:
  - Default (no flag): inline only the fonts in `KEEP_FONTS` (the FontAwesome
    icon font), neutralizing every other font under a `fonts/` dir to
    `url(data:,)`. Text fonts fall back to the system sans-serif. ~0.3MB.
  - `--drop-fonts`: inline NO local font (icon font included). `.build_docs.sh`
    passes this, dropping another ~0.1MB (~30%) → `README.html` ~0.24MB. The only
    cost is the FontAwesome admonition/nav icons, which this static preview (the
    README.md is canonical) does not need.
  Breakdown of the ~0.24MB file: ~65% inlined theme CSS, ~25% page content, the
  rest images. The inlined CSS is intrinsic to a self-contained single file —
  the bulk that remains after dropping fonts.

Steps:

1. Copy the four bundled scripts from this skill into the **role root**, keeping
   the leading dots (then `chmod +x` the shell script):
   - `scripts/build_docs.sh` → `<role>/.build_docs.sh`
   - `scripts/html_to_md.py` → `<role>/.html_to_md.py`
   - `scripts/html_to_singlefile.py` → `<role>/.html_to_singlefile.py`
   - `scripts/merge_set_vars.py` → `<role>/.merge_set_vars.py`
   All are role-agnostic (they derive the role name from the directory), and
   `.build_docs.sh` calls the others by those exact dotted names.
2. Ensure `pandoc` is on `PATH` (a system package); `antsibull-docs`/`sphinx` are
   installed into the venv by the script. The first run needs network.
3. If the role returns variables, create `meta/set_vars_specs.yml` (top-level
   `return:` mapping) and add the `notes` pointer in `argument_specs.yml`. Roles
   that return nothing skip this.
4. Check `meta/main.yml` galaxy_info (author, platforms) so `author`/`attributes`
   match.
5. Run `./.build_docs.sh` from the role root.

## Verification checklist (after every build)

Run from the role root:

```bash
python3 -c "import yaml; yaml.safe_load(open('meta/argument_specs.yml')); print('argspec OK')"
# if the role returns variables, set_vars_specs.yml must parse and merge cleanly:
python3 -c "import yaml; d=yaml.safe_load(open('meta/set_vars_specs.yml')); assert 'return' in d; print('set_vars OK')"
./.build_docs.sh                 # exits 0, no antsibull warnings/errors
grep -c '\`' README.md           # -> 0  (no escaped backticks = all markup converted)
grep -c '\[' README.md           # -> 0  (no escaped link brackets)
grep -c '<div' README.md         # -> 0  (no embedded divs)
grep -c 'set_vars_specs' README.md   # -> 0  (pointer note must NOT leak into output)
grep -oE '^### (Synopsis|Parameters|Attributes|Notes|Examples|Authors|Return Variables)' README.md  # list present sections
```

`Synopsis` and `Parameters` must always be present. The rest appear only if you
populated the corresponding field — confirm the sections you *intended* are there
and that none you deliberately omitted (e.g. `Notes`) leaked back in. If the role
returns variables, `Return Variables` must be present (and the pointer note must
*not* leak — the grep above returns 0).

Confirm the tables survive Galaxy's sanitizer (padding is stripped; output
unchanged):

```bash
python3 - <<'PY'
import markdown, nh3
tags={"h1","h2","h3","h4","h5","h6","b","i","strong","em","tt","p","br","span",
      "div","blockquote","code","pre","hr","ul","ol","li","dd","dt","img","a",
      "sub","sup","table","thead","th","tr","td"}
out=nh3.clean(markdown.markdown(open("README.md").read(),extensions=["extra"]),
              tags=tags, attributes={"*":{"id"},"img":{"src","alt","title"},
              "a":{"href","alt","title"}}, strip_comments=True)
print("tables:",out.count("<table"),"| embedded div:",out.count("<div"))
PY
# expect: tables: 2 | embedded div: 0
```

## Step-by-step workflow

1. Read the hand-written `README.md` in full; inventory its sections, every
   variable (type/default/choices), every warning/requirement/caveat, every
   example, and every backtick / link. Keep this inventory as the no-loss
   checklist for step 7.
2. Read the existing `meta/argument_specs.yml` (the option tree) and
   `meta/main.yml` (author, platforms, license).
3. Map README content into the fields per the table above: summary + prose →
   `description`; low-level internals → `notes`; variables → `options` (with
   `type`, `choices`, `default`, and a real `description` for every option);
   returned/output variables → `return:` in `meta/set_vars_specs.yml` (plus the
   `notes` pointer); playbooks → `examples` (copy representative ones verbatim,
   ~8-10, swapping secrets for vault references); authors/platforms →
   `author`/`attributes`.
4. As you map the prose, tighten it to technical-documentation standards (clear,
   concise, unambiguous, active voice, simple tenses) — same meaning, better
   wording. See "Preserve content, improve prose".
5. Convert **all** inline markup to `C`/`V`/`O`/`L`/`B` macros, disambiguating
   per occurrence. Watch the gotchas above.
6. Copy the build scripts, run `./.build_docs.sh`, and run the full verification
   checklist. Rebuild until it is clean.
7. Reconcile the generated `README.md` against the step-1 inventory: confirm every
   variable, default, choice, warning, requirement, caveat, and example is still
   present. Anything missing is a conversion bug — fix the spec and rebuild.
8. Do not commit or push unless explicitly asked.
