"""
file_utils.py
Shared utilities for file I/O operations across modules.
"""

import os


def ensure_files(*files):
    """Ensure that the specified files exist, creating them if necessary."""
    # Allow a single list or tuple as argument
    if len(files) == 1 and isinstance(files[0], (list, tuple)):
        files = files[0]

    for f in files:
        if not os.path.exists(f):
            open(f, "a").close()


def read_lines(file):
    """Read non-empty lines from a file."""
    if not os.path.exists(file):
        open(file, "a").close()
    with open(file, "r", encoding="utf-8") as fh:
        return [l.strip() for l in fh if l.strip()]


def write_lines(file, lines):
    """Write lines to a file."""
    with open(file, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + ("\n" if lines else ""))


def next_id(lines):
    """Calculate the next available ID from existing lines."""
    if not lines:
        return "1"
    return str(max([int(l.split("|", 1)[0]) for l in lines] + [0]) + 1)
