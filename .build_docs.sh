#!/usr/bin/env bash
# Build the README files for this role from meta/argument_specs.yml.
#
# antsibull-docs turns argument_specs.yml into RST, Sphinx renders that RST to
# text and HTML (the same way the official Ansible website builds its docs),
# and pandoc converts the HTML to Markdown. Requires antsibull-docs, sphinx
# and pandoc on PATH.
#
# The script creates these at the repo root:
#   README.md    - Markdown page for Ansible Galaxy and Red Hat Automation Hub,
#                  which display only Markdown. GitHub renders it too.
#   README.txt   - plain text page, readable in any editor
#   README.rst   - the RST antsibull produces (renders fully only with the
#                  Sphinx + antsibull build; generic RST viewers and GitHub
#                  drop its tables, so README.txt is the safe plain read)
#   README.html  - link to the full styled page in sphinx_html/
#   sphinx_html/ - the Sphinx HTML output (the page plus its _static assets)
#
# Markdown is produced from the Sphinx HTML with pandoc. antsibull has no
# Markdown output and Sphinx has no Markdown builder that understands
# antsibull's option tables, so we convert the finished HTML instead. The
# Parameters and Attributes tables are too complex for Markdown pipe tables,
# so they stay as HTML tables; Galaxy, Automation Hub and GitHub all render
# HTML tables in Markdown (they drop the CSS classes, so the tables show
# unstyled but complete).
#
# NOTE: the HTML output (README.html + sphinx_html/) is included here only
# to preview the styled page in the draft PR. Long term, the full styled
# site is built once for the whole fedora.linux_system_roles collection,
# not per role, to keep each role repo small. README.html is a link, so
# commit the sphinx_html folder with it or the link will not resolve.
#
# antsibull-docs works with collections only. This repo has one role and
# is not a collection, so we first copy the role into a temporary
# fedora.linux_system_roles collection. Inside the real collection you do
# not need this step.
#
# Usage: ./.build_docs.sh

set -euo pipefail

for tool in antsibull-docs sphinx-build pandoc; do
    command -v "$tool" >/dev/null 2>&1 || { echo "error: $tool not found on PATH" >&2; exit 1; }
done

ROLE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROLE_NAME="$(basename "$ROLE_DIR")"
OUT_DIR="$ROLE_DIR/sphinx_html"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# Copy this single role into a temporary collection.
COLL="$WORK/collections/ansible_collections/fedora/linux_system_roles"
mkdir -p "$COLL/roles"
ln -s "$ROLE_DIR" "$COLL/roles/$ROLE_NAME"
cat > "$COLL/galaxy.yml" <<EOF
namespace: fedora
name: linux_system_roles
version: 1.0.0
readme: README.md
authors: [Linux System Roles]
EOF
echo "# linux_system_roles" > "$COLL/README.md"
export ANSIBLE_COLLECTIONS_PATH="$WORK/collections"

# antsibull makes the config files it needs: conf.py, antsibull-docs.cfg.
mkdir -p "$WORK/site"
antsibull-docs sphinx-init --use-current --squash-hierarchy \
    --dest-dir "$WORK/site" fedora.linux_system_roles

cd "$WORK/site"

# 1. antsibull turns argument_specs.yml into RST (same command as its build.sh).
chmod og-w rst   # antsibull-docs wants this directory writable only by its owner
antsibull-docs --config-file antsibull-docs.cfg collection \
    --cleanup everything --use-current --squash-hierarchy \
    --dest-dir rst fedora.linux_system_roles
cp "rst/${ROLE_NAME}_role.rst" "$ROLE_DIR/README.rst"

# Ship only the rendered page, not its RST source. By default Sphinx copies
# the .rst files into _sources/ and adds a "Show Source" link; turn both off.
printf '\nhtml_copy_source = False\nhtml_show_sourcelink = False\n' >> conf.py

# 2. Sphinx renders the RST to plain text.
sphinx-build -b text -q -c . rst text
cp "text/${ROLE_NAME}_role.txt" "$ROLE_DIR/README.txt"

# 3. Sphinx renders the RST to the styled HTML site (for the draft PR preview).
sphinx-build -M html rst build -q -c .
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"
cp -r build/html/. "$OUT_DIR"             # styled page plus its _static assets
rm -rf "$OUT_DIR/_sources"                # empty leftover dir (RST source is not shipped)
ln -sfn "sphinx_html/${ROLE_NAME}_role.html" "$ROLE_DIR/README.html"

# 4. pandoc turns the HTML page into Markdown for Galaxy / Automation Hub.
# We feed pandoc the page body only, and clean up a few Sphinx-isms so the
# Markdown renders cleanly through Galaxy's markdown + sanitizer pipeline:
#   - Sphinx splits inline code into one <span class="pre"> per word; we unwrap
#     those so each literal becomes a single clean `code` span.
#   - pandoc wraps sections in <div> and adds empty permalink/anchor tags;
#     Markdown does not process text inside block-level <div>, so we drop the
#     wrapper divs and anchor junk (the HTML tables we want to keep have none).
python3 - "build/html/${ROLE_NAME}_role.html" "$WORK/body.html" <<'PY'
import re, sys
html = open(sys.argv[1], encoding="utf-8").read()
start = html.find('<div role="main"')
depth = 0
end = None
for m in re.compile(r'<(/?)div\b', re.I).finditer(html, start):
    depth += -1 if m.group(1) else 1
    if depth == 0:
        end = html.find('</div>', m.start()) + 6
        break
body = html[start:end]
body = re.sub(r'<span class="pre">(.*?)</span>', r'\1', body, flags=re.S)

# The Parameters table shows nesting with a CSS-indented class that the Galaxy
# sanitizer strips, so child options would look top-level. Encode the nesting
# as text instead: the option's anchor path (parent/child/grandchild) tells us
# the depth, so we prefix nested option titles with indentation and a marker.
def indent_nested(m):
    depth = m.group("path").count("/")
    if not depth:
        return m.group(0)
    return m.group("head") + "&nbsp;" * (4 * depth) + "↳ " + m.group("strong")
body = re.sub(
    r'(?P<head><div class="ansibleOptionAnchor" id="parameter-[^"]*?--(?P<path>[^"]*)"></div>'
    r'<p class="ansible-option-title"[^>]*>)(?P<strong><strong>)',
    indent_nested, body)

open(sys.argv[2], "w", encoding="utf-8").write(body)
PY
pandoc -f html -t gfm --wrap=none "$WORK/body.html" -o "$WORK/README.md"
python3 - "$WORK/README.md" "$ROLE_DIR/README.md" <<'PY'
import re, sys
md = open(sys.argv[1], encoding="utf-8").read()
md = re.sub(r'</?div[^>]*>\n?', '', md)                               # wrapper divs
md = re.sub(r'<span[^>]*class="target"[^>]*></span>\n?', '', md)      # empty anchors
md = re.sub(r'<a[^>]*headerlink[^>]*>.*?</a>', '', md)                # permalink icons
md = re.sub(r'<a[^>]*toc-backref[^>]*>(.*?)</a>', r'\1', md, flags=re.S)  # clean headings
md = re.sub(r'\n{3,}', '\n\n', md)
open(sys.argv[2], "w", encoding="utf-8").write(md)
PY

echo "MD  : $ROLE_DIR/README.md"
echo "Text: $ROLE_DIR/README.txt"
echo "RST : $ROLE_DIR/README.rst"
echo "HTML: $ROLE_DIR/README.html -> sphinx_html/${ROLE_NAME}_role.html"
