#!/usr/bin/env bash
# Build the README files for this role from meta/argument_specs.yml.
#
# antsibull-docs turns argument_specs.yml into RST, Sphinx renders that RST to
# HTML (the same way the official Ansible website builds its docs), and pandoc
# converts the HTML to Markdown. All three are installed from PyPI into a venv,
# so no system packages are required.
#
# The script creates these at the repo root:
#   README.md    - the role's main README. People read it directly as plain
#                  text in the repo, and Markdown viewers render it: GitHub,
#                  Ansible Galaxy and Red Hat Automation Hub (the last two
#                  display role docs only as Markdown). This is the canonical
#                  README; it supersedes the plain-text and RST renderings,
#                  which are intentionally not emitted.
#   README.html  - a single, self-contained styled preview of the page. All CSS
#                  and the FontAwesome icon font are inlined as data: URIs, the
#                  JavaScript is dropped, and the docsite chrome (collection
#                  sidebar/tree, breadcrumb, prev/next) is hidden, so it is just
#                  this role's page with zero in-repo dependencies (no
#                  sphinx_html/ or _static/ to commit). See .html_to_singlefile.py.
#
# RST is still produced internally (antsibull emits it and Sphinx consumes it to
# build the HTML) but is not copied out as README.rst.
#
# Markdown is produced from the Sphinx HTML by the .html_to_md.py helper (which
# calls pandoc). antsibull has no Markdown output and Sphinx has no Markdown
# builder that understands antsibull's option tables, so we convert the finished
# HTML instead. The Parameters and Attributes tables become real Markdown pipe
# tables (Galaxy strips the CSS classes antsibull uses to indent nested options,
# so .html_to_md.py encodes the nesting as dot markers in the Parameter column).
#
# antsibull-docs works with collections only. This repo has one role and
# is not a collection, so we first copy the role into a temporary
# fedora.linux_system_roles collection. Inside the real collection you do
# not need this step.
#
# Usage: ./.build_docs.sh
#
# NOTE: rendering a role's native return: key (the "Return Variables" table) is
# not yet in a released antsibull-docs. Until it is, this script builds with the
# patched antsibull-docs from the fork branch, installed into a dedicated venv
# (see below). Drop this once role return: support ships upstream and switch back
# to the released antsibull-docs.

set -euo pipefail

# Build with the patched antsibull-docs from the fork branch, installed into a
# dedicated venv that is created once and reused on later runs. Override the
# location with ANTSIBULL_RV_VENV; force a refresh by deleting that directory.
# First run needs network. Everything comes from PyPI into the venv, so no
# system packages are required.
ANTSIBULL_RV_SPEC='antsibull-docs @ git+https://github.com/spetrosi/antsibull-docs@role-return-values'
ANTSIBULL_RV_VENV="${ANTSIBULL_RV_VENV:-${XDG_CACHE_HOME:-$HOME/.cache}/lsr-antsibull-docs}"
# Install if the venv is missing antsibull-docs or the pandoc symlink we add below.
if [ ! -x "$ANTSIBULL_RV_VENV/bin/antsibull-docs" ] || [ ! -e "$ANTSIBULL_RV_VENV/bin/pandoc" ]; then
    echo "Installing patched antsibull-docs and pandoc into $ANTSIBULL_RV_VENV ..." >&2
    python3 -m venv "$ANTSIBULL_RV_VENV"
    "$ANTSIBULL_RV_VENV/bin/pip" install --quiet --upgrade pip
    "$ANTSIBULL_RV_VENV/bin/pip" install --quiet \
        "$ANTSIBULL_RV_SPEC" ansible-pygments sphinx sphinx-ansible-theme pypandoc-binary
    # The pandoc executable lives inside the pypandoc package, so link it onto
    # the venv bin (prepended to PATH below).
    ln -sf "$("$ANTSIBULL_RV_VENV/bin/python" -c 'import pypandoc; print(pypandoc.get_pandoc_path())')" \
        "$ANTSIBULL_RV_VENV/bin/pandoc"
fi
PATH="$ANTSIBULL_RV_VENV/bin:$PATH"

for tool in antsibull-docs sphinx-build pandoc; do
    command -v "$tool" >/dev/null 2>&1 || { echo "error: $tool not found on PATH" >&2; exit 1; }
done

ROLE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROLE_NAME="$(basename "$ROLE_DIR")"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# Copy this single role into a temporary collection. The role is mirrored with
# symlinks (so the committed tree is never modified) EXCEPT for
# meta/argument_specs.yml: the committed spec intentionally has no return: key
# (it points at meta/set_vars_specs.yml via a note, to stay accepted by the
# released ansible-lint role-arg-spec schema). .merge_set_vars.py writes a
# merged argument_specs.yml that restores return: from set_vars_specs.yml and
# drops that pointer note, and antsibull renders the "Return Variables" table
# from this merged copy.
COLL="$WORK/collections/ansible_collections/fedora/linux_system_roles"
ROLE_LINK="$COLL/roles/$ROLE_NAME"
mkdir -p "$ROLE_LINK/meta"
# symlink every top-level entry except meta (which needs a modified copy)
for item in "$ROLE_DIR"/*; do
    name="$(basename "$item")"
    [ "$name" = "meta" ] && continue
    ln -s "$item" "$ROLE_LINK/$name"
done
# symlink every meta entry except argument_specs.yml, which we generate below
for item in "$ROLE_DIR"/meta/*; do
    name="$(basename "$item")"
    [ "$name" = "argument_specs.yml" ] && continue
    ln -s "$item" "$ROLE_LINK/meta/$name"
done
# generate the merged argument_specs.yml (return: restored, pointer note dropped)
python3 "$ROLE_DIR/.merge_set_vars.py" \
    "$ROLE_DIR/meta/argument_specs.yml" \
    "$ROLE_DIR/meta/set_vars_specs.yml" \
    "$ROLE_LINK/meta/argument_specs.yml"
# version is mandatory but only used for the "part of the collection" note;
# leave it empty so antsibull omits the version from that note (this per-role
# build has no meaningful collection version).
cat > "$COLL/galaxy.yml" <<EOF
namespace: fedora
name: linux_system_roles
version: ""
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
# The RST is a build intermediate (Sphinx input below); it is not copied out.
chmod og-w rst   # antsibull-docs wants this directory writable only by its owner
antsibull-docs --config-file antsibull-docs.cfg collection \
    --cleanup everything --use-current --squash-hierarchy \
    --dest-dir rst fedora.linux_system_roles

# Ship only the rendered page, not its RST source. By default Sphinx copies
# the .rst files into _sources/ and adds a "Show Source" link; turn both off.
printf '\nhtml_copy_source = False\nhtml_show_sourcelink = False\n' >> conf.py

# 2. Sphinx renders the RST to the styled HTML site.
sphinx-build -M html rst build -q -c .

# 3. Collapse the Sphinx site (page + its _static tree) into ONE self-contained
# README.html at the repo root: .html_to_singlefile.py inlines the CSS and images
# as data: URIs, drops the JavaScript, and hides the docsite chrome (the
# collection sidebar/tree, breadcrumb and prev/next nav) so only this role's page
# remains. No sphinx_html/ directory and no _static assets are committed --
# README.html has zero in-repo dependencies. --drop-fonts drops all local fonts
# (including the FontAwesome icon font) to keep README.html small; the only cost
# is the admonition/nav icons, which this static preview does not need (text
# falls back to system fonts).
python3 "$ROLE_DIR/.html_to_singlefile.py" --drop-scripts --standalone --drop-fonts \
    "build/html/${ROLE_NAME}_role.html" "$ROLE_DIR/README.html"

# 4. .html_to_md.py turns the HTML page into the main README.md (it calls pandoc
# for the prose and rebuilds the option tables as pipe tables).
python3 "$ROLE_DIR/.html_to_md.py" \
    "build/html/${ROLE_NAME}_role.html" "$ROLE_DIR/README.md"

echo "MD  : $ROLE_DIR/README.md"
echo "HTML: $ROLE_DIR/README.html (single self-contained file)"
