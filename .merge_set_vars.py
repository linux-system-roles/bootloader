#!/usr/bin/env python3
"""Merge meta/set_vars_specs.yml back into argument_specs.yml for doc builds.

The role keeps the variables it returns in meta/set_vars_specs.yml under a
``return:`` key, and only points at that file from a note in
meta/argument_specs.yml. That keeps argument_specs.yml accepted by the released
ansible-lint role-arg-spec schema, which does not yet allow the native
``return:`` key. (The separate file is not matched by that schema, so it may use
the key freely.)

To render the "Return Variables" table, the doc build (.build_docs.sh) needs the
data back under ``return:`` in argument_specs.yml. This script writes a merged
copy of argument_specs.yml that:

  * adds argument_specs.main.return from set_vars_specs.yml's ``return:`` key,
  * drops the note that points readers at meta/set_vars_specs.yml.

The committed files are never touched; the merged YAML is written to the
destination path given on the command line (a throwaway copy inside the build's
temporary collection).

Usage:
    .merge_set_vars.py ARGUMENT_SPECS SET_VARS_SPECS DEST
"""

import sys

import yaml

# Any note containing this marker is the pointer to the set_vars file; it is
# removed from the merged copy because that copy carries the data natively.
POINTER_MARKER = "set_vars_specs.yml"


def main(argv):
    if len(argv) != 4:
        sys.exit(f"usage: {argv[0]} ARGUMENT_SPECS SET_VARS_SPECS DEST")
    argument_specs_path, set_vars_specs_path, dest_path = argv[1:]

    with open(argument_specs_path, encoding="utf-8") as specs_file:
        specs = yaml.safe_load(specs_file)
    with open(set_vars_specs_path, encoding="utf-8") as set_vars_file:
        set_vars = yaml.safe_load(set_vars_file)

    entry_points = specs["argument_specs"]
    returned = set_vars["return"]

    for entry_point in entry_points.values():
        # Inject the returned variables as the native return: key.
        entry_point["return"] = returned
        # Drop the note pointing at meta/set_vars_specs.yml.
        notes = entry_point.get("notes")
        if notes:
            notes = [n for n in notes if POINTER_MARKER not in n]
            if notes:
                entry_point["notes"] = notes
            else:
                del entry_point["notes"]

    with open(dest_path, "w", encoding="utf-8") as dest_file:
        yaml.safe_dump(
            specs,
            dest_file,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
            width=4096,
        )


if __name__ == "__main__":
    main(sys.argv)
