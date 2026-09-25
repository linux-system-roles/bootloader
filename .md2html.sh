#!/bin/bash
# Convert a Markdown file to HTML with the ansible/sphinx_rtd_theme styling.
# Usage: md2html.sh INPUT.md [OUTPUT.html]
# Downloads theme CSS files on first run, then caches them locally.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CSS_DIR="$SCRIPT_DIR/.css_cache"

INPUT="${1:?Usage: md2html.sh INPUT.md [OUTPUT.html]}"
OUTPUT="${2:-${INPUT%.md}.html}"
TITLE="$(head -1 "$INPUT" | sed 's/^#\+ *//')"

# Download theme CSS files if not cached
if [ ! -d "$CSS_DIR" ]; then
    mkdir -p "$CSS_DIR"
    BASE_URL="https://linux-system-roles.github.io"
    curl -sL "$BASE_URL/_static/css/theme.css" > "$CSS_DIR/theme.css"
    curl -sL "$BASE_URL/_static/pygments.css" > "$CSS_DIR/pygments.css"
    curl -sL "$BASE_URL/_static/antsibull-minimal.css" > "$CSS_DIR/antsibull-minimal.css"
    curl -sL "$BASE_URL/_static/css/ansible.css" > "$CSS_DIR/ansible.css"
    curl -sL "$BASE_URL/css/main.css" > "$CSS_DIR/main.css"
    # Remove @import from ansible.css since we inline theme.css separately
    sed -i "s/@import 'theme.css';//" "$CSS_DIR/ansible.css"
    echo "Downloaded theme CSS files to $CSS_DIR" >&2
fi

# Generate TOC from markdown headings
generate_toc() {
    local md_file="$1"
    local in_code_block=false
    echo '<div class="wy-menu wy-menu-vertical" data-spy="affix" role="navigation" aria-label="main navigation">'
    echo "<p class=\"caption\" role=\"heading\"><span class=\"caption-text\">${TITLE}</span></p>"
    echo '<ul class="current">'

    local prev_level=0
    local open_uls=0

    while IFS= read -r line; do
        # Skip code blocks
        if [[ "$line" =~ ^\`\`\` ]]; then
            if $in_code_block; then
                in_code_block=false
            else
                in_code_block=true
            fi
            continue
        fi
        $in_code_block && continue

        # Match heading lines
        if [[ "$line" =~ ^(#{1,4})\ (.+) ]]; then
            local hashes="${BASH_REMATCH[1]}"
            local text="${BASH_REMATCH[2]}"
            local level=${#hashes}

            # Skip h1 (the title itself) and h5+
            [ "$level" -eq 1 ] && continue
            [ "$level" -gt 4 ] && continue

            # Create anchor id matching pandoc's algorithm
            local id
            id=$(echo "$text" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 _-]//g; s/ \+/-/g; s/^-//; s/-$//')

            # Close deeper levels
            while [ "$open_uls" -gt 0 ] && [ "$level" -le "$prev_level" ]; do
                echo '</ul></li>'
                open_uls=$((open_uls - 1))
                prev_level=$((prev_level - 1))
            done

            if [ "$level" -gt "$prev_level" ] && [ "$prev_level" -gt 0 ]; then
                # Re-open the last li to nest a ul inside it
                # Actually we need to not close the li above
                :
            fi

            echo "<li class=\"toctree-l$((level - 1))\">"
            echo "  <a class=\"reference internal\" href=\"#${id}\">${text}</a>"

            prev_level=$level
        fi
    done < "$md_file"

    # Close any remaining open tags
    while [ "$open_uls" -gt 0 ]; do
        echo '</ul></li>'
        open_uls=$((open_uls - 1))
    done

    # Close all open li tags
    echo '</ul>'
    echo '</div>'
}

# Build TOC
TOC_HTML=$(generate_toc "$INPUT")

# Build self-contained HTML
{
  cat <<HEADER
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${TITLE}</title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&amp;display=swap">
  <style>
HEADER
  cat "$CSS_DIR/theme.css"
  echo ""
  cat "$CSS_DIR/pygments.css"
  echo ""
  cat "$CSS_DIR/antsibull-minimal.css"
  echo ""
  cat "$CSS_DIR/ansible.css"
  echo ""
  cat "$CSS_DIR/main.css"
  cat <<'EXTRA_CSS'
  /* TOC hierarchy: h3 entries indented, smaller, lighter */
  .wy-menu-vertical li.toctree-l2 { padding-left: 1.2em; }
  .wy-menu-vertical li.toctree-l2 a { color: #b3b3b3; font-size: 0.85em; }
  .wy-menu-vertical li.toctree-l2 a:hover { color: #fff; }
  /* h4 entries: further indented */
  .wy-menu-vertical li.toctree-l3 { padding-left: 2.4em; }
  .wy-menu-vertical li.toctree-l3 a { color: #999; font-size: 0.8em; }
  .wy-menu-vertical li.toctree-l3 a:hover { color: #fff; }
  /* Style pandoc code blocks to match rst-content highlight blocks */
  div.sourceCode, pre:not(.sourceCode) {
    border: 1px solid #e1e4e5;
    overflow-x: auto;
    margin: 1px 0 24px;
    background: #fcfcfc;
  }
  div.sourceCode pre, pre:not(.sourceCode) {
    margin: 0;
    padding: 12px;
    font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 0.85em;
    line-height: 1.5;
    white-space: pre;
    background: #fcfcfc;
    border: none;
  }
  code {
    font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 0.875em;
    padding: 2px 5px;
    background: #e8e8e8;
    border: none;
    color: #333;
  }
  .rst-content p code, .rst-content li code, .rst-content blockquote code,
  .rst-content blockquote p code {
    color: #333;
    background: #e8e8e8;
    border: none;
    padding: 2px 5px;
    font-size: 0.875em;
  }
  pre code, div.sourceCode code {
    padding: 0;
    background: none;
    border: none;
    color: inherit;
    font-size: inherit;
  }
  /* Code blocks inside table cells */
  td pre {
    border: 1px solid #e1e4e5;
    background: #f8f8f8;
    padding: 12px;
    margin: 8px 0;
    overflow-x: auto;
    white-space: pre;
  }
  td pre code {
    padding: 0;
    background: none;
    border: none;
    color: #333;
    font-size: 0.85em;
    font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    line-height: 1.5;
  }
  /* Pandoc syntax highlighting (pygments style) */
  pre > code.sourceCode { white-space: pre; position: relative; }
  pre > code.sourceCode > span { display: inline-block; line-height: 1.25; }
  pre > code.sourceCode > span:empty { height: 1.2em; }
  code.sourceCode > span { color: inherit; text-decoration: inherit; }
  div.sourceCode code span.al { color: #ff0000; font-weight: bold; }
  div.sourceCode code span.an { color: #60a0b0; font-weight: bold; font-style: italic; }
  div.sourceCode code span.at { color: #7d9029; }
  div.sourceCode code span.bn { color: #40a070; }
  div.sourceCode code span.bu { color: #008000; }
  div.sourceCode code span.cf { color: #007020; font-weight: bold; }
  div.sourceCode code span.ch { color: #4070a0; }
  div.sourceCode code span.cn { color: #880000; }
  div.sourceCode code span.co { color: #60a0b0; font-style: italic; }
  div.sourceCode code span.cv { color: #60a0b0; font-weight: bold; font-style: italic; }
  div.sourceCode code span.do { color: #ba2121; font-style: italic; }
  div.sourceCode code span.dt { color: #902000; }
  div.sourceCode code span.dv { color: #40a070; }
  div.sourceCode code span.er { color: #ff0000; font-weight: bold; }
  div.sourceCode code span.fl { color: #40a070; }
  div.sourceCode code span.fu { color: #06287e; }
  div.sourceCode code span.im { color: #008000; font-weight: bold; }
  div.sourceCode code span.in { color: #60a0b0; font-weight: bold; font-style: italic; }
  div.sourceCode code span.kw { color: #007020; font-weight: bold; }
  div.sourceCode code span.op { color: #666666; }
  div.sourceCode code span.ot { color: #007020; }
  div.sourceCode code span.pp { color: #bc7a00; }
  div.sourceCode code span.sc { color: #4070a0; }
  div.sourceCode code span.ss { color: #bb6688; }
  div.sourceCode code span.st { color: #4070a0; }
  div.sourceCode code span.va { color: #19177c; }
  div.sourceCode code span.vs { color: #4070a0; }
  div.sourceCode code span.wa { color: #60a0b0; font-weight: bold; font-style: italic; }
  /* Inline code in blockquotes (variable sub-options) - covered by .rst-content rules above */
  /* Ensure clear spacing before headings and visual hierarchy */
  h2, h3, h4, h5, h6 { margin-top: 1.8em; }
  h4 { font-size: 1.1em; }
  /* Ensure sidebar and content render properly in standalone mode */
  .wy-nav-side { position: fixed; top: 0; bottom: 0; left: 0; width: 300px;
                  overflow-y: auto; background: #343131; z-index: 200; }
  .wy-nav-content-wrap { margin-left: 300px; }
  .wy-nav-content { max-width: none; padding: 1.618em 3.236em; }
  .wy-side-nav-search { background: #5bbdbf; padding: 0.809em; }
  .wy-side-nav-search .wy-side-nav-title { font-size: 1.2em; color: #fff; font-weight: 700; display: block; padding: 0.4em 0; }
  @media screen and (max-width: 768px) {
    .wy-nav-side { width: 100%; position: relative; }
    .wy-nav-content-wrap { margin-left: 0; }
  }

  /* ---- Ansible-style parameter tables ---- */
  .rst-content table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1.5em;
  }
  .rst-content table th {
    background: #e3edf7;
    color: #333;
    font-weight: 700;
    text-align: left;
    padding: 8px 12px;
    border: 1px solid #cad4e0;
  }
  .rst-content table td {
    padding: 8px 12px;
    border: 1px solid #e1e4e5;
    vertical-align: top;
  }
  .rst-content table tr:nth-child(even) > td {
    background: #f9fbfd;
  }
  /* Variable name column: fixed width */
  .rst-content table td:first-child {
    width: 180px;
    min-width: 140px;
    white-space: nowrap;
  }
  /* Type in purple (Ansible style) */
  .rst-content table td code {
    color: #6a0dad;
    background: none;
    border: none;
    padding: 0;
    font-size: 0.85em;
  }
  /* "required" marker in red */
  .rst-content table td b:last-of-type {
    /* don't override variable name bold */
  }
  .rst-content table td:first-child > code {
    color: #6a0dad;
  }
  /* Nested sub-option tables */
  .rst-content table table {
    margin-top: 8px;
    margin-bottom: 0;
    border-left: 3px solid #d0d7de;
  }
  .rst-content table table th {
    display: none;  /* no repeated headers in sub-tables */
  }
  .rst-content table table td {
    border-color: #e8ecf0;
  }
  .rst-content table table td:first-child {
    padding-left: 12px;
  }
  /* Deeper nesting */
  .rst-content table table table {
    border-left: 3px solid #dde3e9;
  }
  /* Description cell: restore code styling for inline code in descriptions */
  .rst-content table td:last-child code {
    color: #333;
    background: #e8e8e8;
    border: none;
    padding: 1px 4px;
    font-size: 0.85em;
  }
  /* But keep purple for type codes in Variable column */
  .rst-content table td:first-child code {
    color: #6a0dad;
    background: none;
    border: none;
    padding: 0;
  }
EXTRA_CSS
  cat <<MIDDLE
  </style>
</head>
<body class="wy-body-for-nav">
  <div class="wy-grid-for-nav">
    <nav data-toggle="wy-nav-shift" class="wy-nav-side">
      <div class="wy-side-scroll">
        <div class="wy-side-nav-search">
          <a href="#" class="wy-side-nav-title">${TITLE}</a>
        </div>
        <div class="wy-side-nav-search-content">
${TOC_HTML}
        </div>
      </div>
    </nav>
    <section data-toggle="wy-nav-shift" class="wy-nav-content-wrap">
      <div class="wy-nav-content">
        <div class="rst-content">
          <div role="main" class="document" itemscope="itemscope" itemtype="http://schema.org/Article">
            <div itemprop="articleBody">
MIDDLE
  pandoc "$INPUT" -f markdown -t html5 --wrap=none --highlight-style=pygments
  cat <<FOOTER
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</body>
</html>
FOOTER
} > "$OUTPUT"

echo "Generated $OUTPUT"
