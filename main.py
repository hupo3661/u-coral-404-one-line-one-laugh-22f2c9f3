#!/usr/bin/env python3
"""One Line, One Laugh - writes one funny line to /output/entry.txt.

Writes a single sentence of at most 200 characters to
``/output/entry.txt``, for make.fun's "One Line, One Laugh" bounty.
Pure standard library and fully deterministic: no randomness, no
network access, no clock, no input files. Running it twice produces
byte-identical output.

Layout of this program
----------------------
* :data:`LINE` -- the single line being entered, kept verbatim.
* :func:`check_not_empty`, :func:`check_single_line`,
  :func:`check_no_edge_whitespace`, :func:`check_length`,
  :func:`check_text_safe` -- one small gate check each, so a failing
  rule names itself in the error message.
* :func:`validate` -- runs every gate check in order.
* :func:`resolve_output_path` -- where the file goes, honouring the
  ``OUTPUT_PATH`` override used by the harness.
* :func:`write_line` / :func:`verify_written` -- write the file,
  then read it back and prove it matches, byte for byte.
* :func:`main` -- glue: validate, write, verify, report.
"""

import os
import sys

LINE = "I told my password manager I forgot my master password, and it asked me to prove I'm me by remembering the one thing I hired it to remember."

MAX_CHARS = 200


def check_not_empty(line: str) -> None:
    """Reject blank or whitespace-only entries."""
    if not line.strip():
        raise ValueError("entry must not be empty or only whitespace")


def check_single_line(line: str) -> None:
    """Reject anything that is not exactly one line of text."""
    if "\n" in line or "\r" in line:
        raise ValueError("entry must be a single line (no line breaks)")


def check_no_edge_whitespace(line: str) -> None:
    """Reject leading/trailing spaces that would be invisible in output."""
    if line != line.strip():
        raise ValueError("entry must not start or end with whitespace")


def check_length(line: str) -> None:
    """Enforce the competition's character gate, at most 200 chars."""
    if len(line) > MAX_CHARS:
        raise ValueError(
            f"entry is {len(line)} chars, over the {MAX_CHARS} limit"
        )


def check_text_safe(line: str) -> None:
    """Reject control characters and confirm the text is valid UTF-8."""
    line.encode("utf-8")  # raises UnicodeEncodeError if not valid UTF-8
    bad = [c for c in line if ord(c) < 0x20]
    if bad:
        raise ValueError(
            "entry contains control characters: "
            + ", ".join(f"U+{ord(c):04X}" for c in bad)
        )


def check_word_count(line: str) -> None:
    """Sanity check: a one-liner needs at least two words to land a joke."""
    if len(line.split()) < 2:
        raise ValueError("entry needs at least two words to be a joke")


def validate(line: str) -> None:
    """Run every gate check; raise ValueError naming the first failure."""
    check_not_empty(line)
    check_single_line(line)
    check_no_edge_whitespace(line)
    check_length(line)
    check_text_safe(line)
    check_word_count(line)


def resolve_output_path() -> str:
    """Return the path of the file to write, creating its directory."""
    output_path = os.environ.get("OUTPUT_PATH", "/output/entry.txt")
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    return output_path


def write_line(line: str, output_path: str) -> None:
    """Write the line exactly as-is, as UTF-8 text with no newline."""
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write(line)


def verify_written(line: str, output_path: str) -> None:
    """Read the file back and prove it is exactly what we intended."""
    with open(output_path, encoding="utf-8") as f:
        written = f.read()
    if written != line:
        raise ValueError("written entry does not match LINE")
    validate(written)


def main() -> int:
    """Validate, write, verify, and report. Returns a process exit code."""
    validate(LINE)
    output_path = resolve_output_path()
    write_line(LINE, output_path)
    verify_written(LINE, output_path)
    words = len(LINE.split())
    print(f"wrote {len(LINE)} chars ({words} words) to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
