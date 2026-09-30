#!/usr/bin/env bash
# Build a plain-text README for this role from meta/argument_specs.yml.
#
# This uses only standard tools. antsibull-docs turns argument_specs.yml
# into RST, and Sphinx renders that RST to plain text. This is the same
# way the official Ansible website builds its docs, only the text output.
#
# The script creates these at the repo root:
#   README.txt   - plain text page, readable in any editor
#   README.rst   - the RST antsibull produces (renders fully only with the
#                  Sphinx + antsibull build; generic RST viewers and GitHub
#                  drop its tables, so README.txt is the safe plain read)
#   README.html  - link to the full styled page in sphinx_html/
#   sphinx_html/ - the Sphinx HTML output (the page plus its _static assets)
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

echo "Text: $ROLE_DIR/README.txt"
echo "RST : $ROLE_DIR/README.rst"
echo "HTML: $ROLE_DIR/README.html -> sphinx_html/${ROLE_NAME}_role.html"
