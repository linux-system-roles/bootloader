#!/usr/bin/env python3
"""Generate README.md from meta/main.yml, meta/argument_specs.yml, and meta/docs_specs.yml."""

import argparse
import os
import re
import sys

import yaml
from jinja2 import Environment, FileSystemLoader

PLATFORM_PATTERNS = {
    "el": "RHEL and CentOS",
    "fedora": "Fedora",
    "sle": "SLE",
    "debian": "Debian",
    "ubuntu": "Ubuntu",
}


def load_yaml(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def extract_platforms(galaxy_tags):
    """Extract supported platforms from galaxy_tags like el7, el8, fedora."""
    platforms = {}
    for tag in galaxy_tags:
        for prefix, label in PLATFORM_PATTERNS.items():
            if tag == prefix:
                platforms.setdefault(label, [])
                break
            match = re.match(rf"^{prefix}(\d+)$", tag)
            if match:
                platforms.setdefault(label, []).append(match.group(1))
                break
    for label in platforms:
        platforms[label].sort(key=lambda v: int(v) if v.isdigit() else 0)
    return platforms


def get_vars_for_tags(specs, include_tags, exclude_vars=None):
    """Return an ordered dict of variables whose doc_tags intersect include_tags."""
    exclude_vars = set(exclude_vars or [])
    options = specs.get("argument_specs", {}).get("main", {}).get("options", {})
    result = {}
    for var_name, var_details in options.items():
        if var_name in exclude_vars:
            continue
        var_tags = var_details.get("doc_tags", [])
        if set(var_tags) & set(include_tags):
            result[var_name] = var_details
    return result


def _linkify_variables(text, var_names):
    """Replace `var_name` with [`var_name`](#var_name) in prose text."""
    lines = text.split('\n')
    result = []
    in_code_block = False
    for line in lines:
        if line.startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            continue
        if in_code_block:
            result.append(line)
            continue
        # Skip heading lines that define the variable (avoid self-links)
        if line.startswith('#'):
            result.append(line)
            continue
        for var in var_names:
            # Replace `var` with [`var`](#var) but not if already linked
            line = line.replace(
                '`' + var + '`',
                '[`' + var + '`](#' + var + ')'
            )
            # Fix double-linking: [[`var`](#var)](#var) -> [`var`](#var)
            double = '[`' + var + '`](#' + var + ')'
            line = line.replace('[' + double + '](#' + var + ')', double)
        result.append(line)
    return '\n'.join(result)


def _md_code_to_html(text):
    """Convert markdown code fences to HTML <pre><code> for use inside table cells."""
    lines = text.split('\n')
    result = []
    in_code = False
    lang = ''
    code_lines = []
    for line in lines:
        if not in_code and re.match(r'^```(\w*)$', line):
            in_code = True
            lang = re.match(r'^```(\w*)$', line).group(1)
            code_lines = []
            continue
        if in_code and line.strip() == '```':
            in_code = False
            cls = f' class="language-{lang}"' if lang else ''
            result.append(f'<pre><code{cls}>')
            result.append('\n'.join(code_lines))
            result.append('</code></pre>')
            continue
        if in_code:
            code_lines.append(line)
            continue
        result.append(line)
    return '\n'.join(result)


def _one_sentence_per_line(text):
    """Break paragraph text so each sentence starts on its own line."""
    lines = text.split('\n')
    result = []
    in_code_block = False
    for line in lines:
        if line.startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            continue
        if in_code_block:
            result.append(line)
            continue
        # Skip headings, list items, blank lines, metadata lines, blockquotes
        if (not line or line.startswith('#') or line.startswith('*')
                or line.startswith('-') or line.startswith('  ')
                or line.startswith('[![') or line.startswith('|')
                or line.startswith('>')):
            result.append(line)
            continue
        # Split sentences: break after ". " or ".) " followed by a
        # capital letter or backtick, but not inside e.g. "e.g." patterns
        parts = re.split(r'(?<=[.!?])\s+(?=[A-Z`])', line)
        result.extend(parts)
    return '\n'.join(result)


def render_readme(role_dir, template_dir):
    meta = load_yaml(os.path.join(role_dir, "meta", "main.yml"))
    specs = load_yaml(os.path.join(role_dir, "meta", "argument_specs.yml"))
    docs = load_yaml(os.path.join(role_dir, "meta", "docs_specs.yml"))
    collection_reqs = load_yaml(
        os.path.join(role_dir, "meta", "collection-requirements.yml")
    )

    env = Environment(
        loader=FileSystemLoader(template_dir),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["intersect"] = lambda a, b: list(set(a) & set(b))
    env.filters["md_to_html"] = _md_code_to_html
    env.globals["get_vars_for_tags"] = lambda tags, exclude=None: get_vars_for_tags(
        specs, tags, exclude
    )

    template = env.get_template("README.md.j2")

    role_name_fallback = os.path.basename(os.path.abspath(role_dir))
    galaxy_tags = meta.get("galaxy_info", {}).get("galaxy_tags", [])
    platforms = extract_platforms(galaxy_tags)

    readme = template.render(
        meta=meta,
        specs=specs,
        docs=docs,
        collection_reqs=collection_reqs,
        role_name_fallback=role_name_fallback,
        platforms=platforms,
    )

    readme = readme.lstrip('\n')
    readme = re.sub(r'\n{3,}', '\n\n', readme)
    # Ensure a blank line before every markdown heading
    readme = re.sub(r'(?<!\n)\n(#{1,6} )', r'\n\n\1', readme)
    # Ensure a blank line before "Sub-options:" labels
    readme = re.sub(r'(?<!\n)\n(Sub-options:)', r'\n\n\1', readme)
    # Convert tight lists to loose lists (blank line between items)
    prev = None
    while prev != readme:
        prev = readme
        readme = re.sub(r'(\n[*-] .+)\n([*-] )', r'\1\n\n\2', readme)
    # One sentence per line for cleaner diffs
    readme = _one_sentence_per_line(readme)
    # Make variable references clickable
    var_names = set(
        specs.get("argument_specs", {}).get("main", {}).get("options", {}).keys()
    )
    # Also collect return variable names from docs_specs
    for section in docs.get("doc_sections", []):
        if section.get("type") == "returns":
            for var in section.get("variables", []):
                var_names.add(var["name"])
    readme = _linkify_variables(readme, var_names)

    output_path = os.path.join(role_dir, "README.md")
    with open(output_path, "w") as f:
        f.write(readme)

    print(f"Generated {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate README.md for an Ansible role")
    parser.add_argument("role_dir", help="Path to the role directory")
    parser.add_argument(
        "--template-dir",
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Path to directory containing README.md.j2",
    )
    args = parser.parse_args()
    render_readme(args.role_dir, args.template_dir)


if __name__ == "__main__":
    main()
