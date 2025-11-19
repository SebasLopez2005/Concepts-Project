# =====================================================
# === Parser Module  (Final Version) ===
# =====================================================
# Authors: Sebastián López, Diego Bonilla, Luis Baeza
# =====================================================

import re
import sys

# -----------------------------------------------------
#  Low-level chord-token parsing
# -----------------------------------------------------

def parse_note(s, pos):
    """
    Parse a note A–G with optional # or b from s[pos:].
    Returns (note_string, new_pos).
    Raises ValueError if no valid note at pos.
    """
    if pos >= len(s) or s[pos] not in "ABCDEFG":
        raise ValueError(f"Expected note at position {pos} in {s!r}")
    note = s[pos]
    pos += 1
    if pos < len(s) and s[pos] in "#b":
        note += s[pos]
        pos += 1
    return note, pos


def parse_chord_token(tok):
    """
    Parse a single chord token like:
        D/E, C/D, B7#9, B-/E, E-7, C^13, E5, B-7/D, etc.

    Returns:
        (root, qual, ext_type, extension, sus, bass, omit3, omit5)

    or:
        None  if this token is "NC" (no chord).
    """
    tok = tok.strip()
    if not tok:
        return None

    # ---- No chord (NC) ----
    if tok.upper() == "NC":
        # For the histogram we completely ignore NC (no chord row)
        return None

    # ---- Slash chords: X.../BASS ----
    bass = ""
    if "/" in tok:
        left, right = tok.split("/", 1)
        tok = left
        # parse bass note (only the letter + accidental)
        try:
            bnote, bpos = parse_note(right, 0)
            bass = bnote
        except ValueError:
            bass = ""

    pos = 0

    # ---- Root note ----
    root, pos = parse_note(tok, pos)

    # ---- Quality: -, +, o (minor, augmented, diminished) ----
    qual = " "
    if pos < len(tok) and tok[pos] in "-+o":
        qual = tok[pos]
        pos += 1

    # ---- Extension type: '^' for maj7 etc. ----
    ext_type = " "
    if pos < len(tok) and tok[pos] == "^":
        ext_type = "^"
        pos += 1

    # ---- Extension number(s) (5, 6, 7, 9, 11, 13, etc.) ----
    extension = 0
    if pos < len(tok) and tok[pos].isdigit():
        start = pos
        while pos < len(tok) and tok[pos].isdigit():
            pos += 1
        try:
            extension = int(tok[start:pos])
        except ValueError:
            extension = 0

    # ---- Parenthetical extension: A6(9), C(13), etc. ----
    if pos < len(tok) and tok[pos] == "(":
        endp = tok.find(")", pos + 1)
        if endp != -1:
            inner = tok[pos + 1:endp]
            if inner.isdigit():
                par_ext = int(inner)
                if extension and par_ext and par_ext != extension:
                    extension = (extension, par_ext)
                elif extension == 0:
                    extension = par_ext
            pos = endp + 1

    # ---- Suspensions and omissions in trailing text ----
    rest = tok[pos:]

    sus = 0
    omit3 = False
    omit5 = False

    # omit3 / no3 / omit5 / no5
    if "no3" in rest:
        omit3 = True
        rest = rest.replace("no3", "")
    if "no5" in rest:
        omit5 = True
        rest = rest.replace("no5", "")
    if "omit3" in rest:
        omit3 = True
        rest = rest.replace("omit3", "")
    if "omit5" in rest:
        omit5 = True
        rest = rest.replace("omit5", "")

    # sus2 / sus4
    if "sus2" in rest:
        sus = 2
        rest = rest.replace("sus2", "")
    elif "sus4" in rest:
        sus = 4
        rest = rest.replace("sus4", "")

    return (root, qual, ext_type, extension, sus, bass, omit3, omit5)


# -----------------------------------------------------
#  Song parser with '%' handling
# -----------------------------------------------------

def parse_song(filepath):
    """
    Returns a list of chord tuples:
        (root, qual, ext_type, extension, sus, bass, omit3, omit5)

    Behavior:
    - Reads a full .txt chord chart (advanced.in style).
    - Ignores a leading meter token like "4/4".
    - Treats '|' as bar separators.
    - Treats '%' as a repeat sign in the chart, but for this
      calculator (to match the basic.out style you’re using
      now) we DO NOT expand or count '%' again; we just
      ignore it as input to the calculator.

    - Ignores NC (no-chord) in the pitch histogram.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Echo original content (like the echo parser)
    print(text, end="")

    # 1) Normalize " X / Y " → "X/Y" so that '/' never becomes its own token
    text = re.sub(r"\s*/\s*", "/", text)

    # 2) Normalize bars: ensure '||' is treated as separate bars
    text = text.replace("||", "| |")

    # 3) Ensure bars are standalone tokens
    text = text.replace("|", " | ")

    tokens = text.split()

    parsed_chords = []
    current_bar_chords = []

    for i, raw_tok in enumerate(tokens):
        tok = raw_tok.strip()
        if not tok:
            # Skip empty tokens defensively
            continue

        # Optional meter at the very beginning: e.g. "4/4"
        if i == 0 and re.match(r"^\d+/\d+$", tok):
            continue

        # Bar boundary: flush current bar into global list
        if tok == "|":
            if current_bar_chords:
                parsed_chords.extend(current_bar_chords)
            current_bar_chords = []
            continue

        # '%' repeat sign:
        # For this calculator version, we are NOT expanding repeats,
        # so we simply ignore '%' as a chord token.
        if tok == "%":
            continue

        # Standalone slash should never appear now, but just in case:
        if tok == "/":
            continue

        # Normal chord token
        chord = parse_chord_token(tok)
        if chord is not None:
            current_bar_chords.append(chord)

    # Flush final bar if there is no trailing '|'
    if current_bar_chords:
        parsed_chords.extend(current_bar_chords)

    return parsed_chords


# -----------------------------------------------------
#  Standalone test driver
# -----------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: Parser.py <input.txt>")
        sys.exit(1)
    fp = sys.argv[1]
    chords = parse_song(fp)
    print(f"\nParsed chords: {len(chords)}")
