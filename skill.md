---
name: readme-to-argument-specs
description: >-
  Convert a linux-system-roles hand-written README.md into a native
  meta/argument_specs.yml (antsibull semantic-markup fields) and generate
  README.md/.txt/.rst/.html from it. Use when asked to "generate role docs
  from argument_specs", "convert the README to argument_specs", add examples /
  notes / attributes to a role's argument_specs, or fix escaped backticks/links
  in a generated role README.
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

- **Pure native.** All documentation content lives in `meta/argument_specs.yml`
  native antsibull fields (`short_description`, `description`, `author`, `notes`,
  `attributes`, `options`, `examples`). No custom templating, no extra metadata
  files. This keeps maintenance low — the goal is to delegate to standard
  antsibull/Sphinx tooling, not to build custom machinery.
- **Lose no content.** The conversion must preserve every fact from the original
  `README.md` — every variable, default, choice, warning, requirement, caveat,
  and example. Dropping information is a bug, not a simplification. See
  "Preserve content, improve prose" below.
- **Generated artifacts are never hand-edited.** `README.md`, `README.html`, and
  `sphinx_html/` are all build outputs. Edit `argument_specs.yml` and rebuild.
- **The only custom piece** is `.html_to_md.py` (antsibull has no Markdown
  output). It is shared verbatim across roles and bundled with this skill.
- **All work is local.** Do not commit or push anything unless the user
  explicitly asks.

## Where content goes (entry point `main`)

| Field | Renders as | Put here |
|---|---|---|
| `short_description` | page subtitle | one-line role summary |
| `description` | **Synopsis** | role summary **and all narrative/operational prose**: providers, requirements, warnings, compatibility, limitations, caveats. One list item = one bullet. |
| `author` | Authors | list of names |
| `notes` | **Notes** | **only low-level, implementation-level details** — variables the role returns, why some variables are intentionally not declared, how fact-dependent defaults resolve. One list item = one bullet. |
| `attributes` | Attributes table | `platform` (with a `platforms:` list), `check_mode`, etc. Every attribute needs a `support:` value. Mirror `meta/main.yml` galaxy_info platforms. |
| `options` | Parameters table | every role variable: `type`, `default`, `choices`, `description`, nested sub-`options`. |
| `examples` | Examples | an `examples: |` literal block of full plays (`name`, `hosts`, `vars`, `roles`). |

**Include a section only when it carries real content.** `short_description`,
`description`, and `options` are effectively always present. `author`, `notes`,
`attributes`, and `examples` are optional — omit the field entirely when there is
nothing genuine to say, rather than emitting an empty or filler section. In
particular, **omit `notes` when the role has no low-level internals or returned
variables** to document; do not pad it with prose that belongs in the Synopsis.

### Synopsis vs Notes — the key split

This was decided deliberately and applied to both `bootloader` and `network`:

- **Synopsis (`description`)** carries everything a reader needs up front,
  including warnings, compatibility, and limitations.
- **Notes** is reserved for the genuinely low-level stuff. In `bootloader` that
  is the variables the role returns (roles have no native `return:` field, so
  they are documented as notes). In `network` there are no returned variables,
  so Notes holds the default-resolution internals (why `network_provider` etc.
  are not declared, why `network_ignore_errors`/`network_force_state_change`
  have no default in `defaults/main.yml`).

If a role sets user-facing output facts, document them in Notes like bootloader:
a `B(Values returned by the role):` lead line, then one `• C(var) — ...` bullet
per returned variable.

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

The pipeline is: antsibull-docs → RST (intermediate) → Sphinx (HTML) →
`.html_to_md.py` (pandoc) → `README.md` (plus `README.html` + `sphinx_html/`).
`README.txt` and `README.rst` are not emitted. The build also trims
`sphinx_html/` to **woff2 fonts only** (the RTD theme bundles Lato, Roboto Slab +
FontAwesome in four formats, ~9MB; woff2 is all modern browsers use), shrinking
the committed preview from ~10MB to ~2.5MB with no visible change.

1. Copy the two bundled scripts from this skill into the **role root**, keeping
   the leading dots:
   - `scripts/build_docs.sh` → `<role>/.build_docs.sh`  (then `chmod +x`)
   - `scripts/html_to_md.py` → `<role>/.html_to_md.py`
   Both are role-agnostic (they derive the role name from the directory), so the
   same copies work for every role. `.build_docs.sh` calls `.html_to_md.py` by
   that exact dotted name.
2. Ensure `antsibull-docs`, `sphinx-build`, and `pandoc` are on `PATH`.
3. Check `meta/main.yml` galaxy_info (author, platforms) so `author`/`attributes`
   match.
4. Run `./.build_docs.sh` from the role root.

## Verification checklist (after every build)

Run from the role root:

```bash
python3 -c "import yaml; yaml.safe_load(open('meta/argument_specs.yml')); print('YAML OK')"
./.build_docs.sh                 # exits 0, no antsibull warnings/errors
grep -c '\`' README.md           # -> 0  (no escaped backticks = all markup converted)
grep -c '\[' README.md           # -> 0  (no escaped link brackets)
grep -c '<div' README.md         # -> 0  (no embedded divs)
grep -oE '^### (Synopsis|Parameters|Attributes|Notes|Examples|Authors)' README.md  # list present sections
```

`Synopsis` and `Parameters` must always be present. The rest appear only if you
populated the corresponding field — confirm the sections you *intended* are there
and that none you deliberately omitted (e.g. `Notes`) leaked back in.

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
   playbooks → `examples` (copy representative ones verbatim, ~8-10, swapping
   secrets for vault references); authors/platforms → `author`/`attributes`.
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
