# =====================================================
# === Parser Module (Echo Parser) =====================
# =====================================================
# Authors: Sebastián López, Diego Bonilla, Luis Baeza
# =====================================================

import sys
import os

# =============== Globals =============================
token = ""          # current character
input_file = None   # file handle
parsed_chords = []  # [(root, qual, ext_type, ext, sus, bass)]

# =============== Lexer ===============================
def get_char():
    return input_file.read(1)

def skip_ws(c):
    while c and c in " \t\r":
        c = get_char()
    return c

def get_token():
    global token
    c = get_char()
    c = skip_ws(c)
    token = c if c else ""

def error(msg):
    print(f"\\nError: {msg}", file=sys.stderr)
    sys.exit(1)

def match(ch, msg=None):
    global token
    if token != ch:
        error(msg or f"'{ch}' expected, got '{token or 'EOF'}'")
    print(ch, end="")
    get_token()

# =============== Notes / Accidentals =================
def read_note():
    """Read a note A-G with optional accidental (#, b, \, Z).
       Normalize '\' -> '#', 'Z' -> 'b' for internal form.
    """
    global token
    if token not in "ABCDEFG":
        error(f"Invalid note letter '{token or 'EOF'}'")
    note = token
    get_token()
    if token in ("#", "b", "\\", "Z"):
        acc = token
        if acc == "\\":
            acc = "#"
        elif acc == "Z":
            acc = "b"
        note += acc
        get_token()
    print(note, end="")
    return note

# =============== Helper consumers ====================
def consume_parentheses():
    """Consume balanced parenthesis groups like (9), (add9)."""
    global token
    while token == "(":
        print("(", end="")
        get_token()
        while token and token != ")":
            print(token, end="")
            get_token()
        match(")", "Missing ')' in parenthetical modifier")

def consume_alpha_num_modifier():
    """Consume alpha+digits words like no3, sus2, maj7 etc."""
    global token
    consumed = False
    while token and token.isalpha():
        consumed = True
        while token and token.isalpha():
            print(token, end="")
            get_token()
        while token and token.isdigit():
            print(token, end="")
            get_token()
    return consumed

def consume_trailing_modifiers():
    """Greedy consumer for (9), no3, sus2, etc., appearing after the core chord."""
    while True:
        before = token
        consume_parentheses()
        did_words = consume_alpha_num_modifier()
        if before == token and not did_words:
            break

# =============== Grammar nodes =======================
def quality():
    """Permissive quality: letters, '+', '-' (dash allowed anywhere until stopper)."""
    global token
    val = ""
    while token and (token.isalpha() or token in {"+", "-"}):
        # stop before a note letter (start of bass without '/')
        if token in "ABCDEFG":
            break
        val += token
        print(token, end="")
        get_token()
    return val

def extensions_and_sus():
    """Parse optional '^', digits for extensions, and allow dash-chains after digits.
       Examples accepted: 7, 9, 11, 13, 5-7, 7-9, 5-, etc.
       Also 'add9' and 'sus2/sus4' in-line.
    """
    global token
    ext_type, ext, sus = "", None, None

    if token == "^":
        ext_type = "^"
        print("^", end="")
        get_token()

    # Base extension number(s)
    if token and token.isdigit():
        while token and token.isdigit():
            print(token, end="")
            get_token()

    # One or more "-<digits_optional>" groups (e.g., -7, -9, or just a trailing '-')
    while token == "-":
        print("-", end="")
        get_token()
        while token and token.isdigit():
            print(token, end="")
            get_token()

    # Optional 'add' N
    if token == 'a':
        buf = ""
        while token and token.isalpha():
            buf += token
            print(token, end="")
            get_token()
        if buf.lower() == "add":
            while token and token.isdigit():
                print(token, end="")
                get_token()

    # Optional 'sus' N
    if token == 's':
        buf = ""
        while token and token.isalpha():
            buf += token
            print(token, end="")
            get_token()
        if buf.lower().startswith("sus"):
            while token and token.isdigit():
                print(token, end="")
                get_token()

    return ext_type, ext, sus

def bass_note_if_any():
    """Bass may be '/<note>' or immediately another note letter (implied slash)."""
    global token
    if token == "/":
        match("/", "'/' expected before bass note")
        return read_note()
    if token in "ABCDEFG":
        return read_note()
    return None

def chord():
    root = read_note()
    qual = quality()
    ext_type, ext, sus = extensions_and_sus()
    consume_trailing_modifiers()
    bass = bass_note_if_any()
    parsed_chords.append((root, qual, ext_type, ext, sus, bass))
    return True

def bar():
    chord()
    while token and token not in "|\n":
        if token == " ":
            print(" ", end="")
            get_token()
            continue
        chord()
    match("|", "'|' expected at end of bar")
    # Allow double bars '||...'
    while token == "|":
        print("|", end="")
        get_token()

def meter():
    x = numerator()
    print(f"{x}", end="")
    match("/", "'/' expected in meter")
    y = denominator()
    print(f"/{y}", end="")

def numerator():
    global token
    if not token.isdigit():
        error("Meter numerator expected")
    num = ""
    while token and token.isdigit():
        num += token
        print(token, end="")
        get_token()
    return int(num)

def denominator():
    global token
    if not token.isdigit():
        error("Meter denominator expected")
    den = ""
    while token and token.isdigit():
        den += token
        print(token, end="")
        get_token()
    return int(den)

def song():
    # optional meter at beginning
    if token and token.isdigit():
        meter()
        if token and token not in ("\n", "|"):
            print(" ", end="")
    while token:
        if token == "\n":
            print()
            get_token()
            continue
        bar()

# =============== Driver ==============================
def parse_song(filepath):
    global input_file, token, parsed_chords
    parsed_chords = []
    with open(filepath, "r", encoding="utf-8") as f:
        input_file = f
        get_token()
        song()
    return parsed_chords

def main():
    if len(sys.argv) != 2:
        print("Usage: Parser.py <input.txt>")
        sys.exit(1)
    filepath = sys.argv[1]
    if not filepath.lower().endswith(".txt"):
        print("Error: Only .txt files are supported")
        sys.exit(1)
    if not os.path.exists(filepath):
        print("Error: cannot open file")
        sys.exit(1)
    chords = parse_song(filepath)
    print(f"\\nTotal parsed chords: {len(chords)}")

if __name__ == "__main__":
    main()


