# =====================================================
# === Parser Module (for Full Parser + Calculator) ====
# =====================================================
# Authors: Sebastián López, Diego Bonilla, Luis Baeza
# =====================================================

import sys
import os

# =====================================================
# === GLOBALS =========================================
# =====================================================
token = ""
input_file = None
parsed_chords = []  # [(root, qual, ext_type, ext, sus, bass)]


# =====================================================
# === TOKEN HANDLING =================================
# =====================================================
def get_token():
    """Read next non-whitespace character."""
    global token
    ch = input_file.read(1)
    while ch and ch in (" ", "\n", "\t"):
        ch = input_file.read(1)
    token = ch if ch else ""


def match(expected, message):
    global token
    if token == expected:
        get_token()
    else:
        error(message)


def error(message):
    print(f"\nParse error: {message}")
    sys.exit(1)


# =====================================================
# === GRAMMAR =========================================
# =====================================================
def parse_input():
    song()
    if token != "":
        error("EOF expected")


def song():
    while token and token != "|":
        bar()
    if token == "|":
        print(token, end="")
        match("|", "| expected")
    else:
        error("| expected at end of song")


def bar():
    if token.isdigit():
        meter()
    chords()
    if token == "|":
        print(token, end="")
        match("|", "| expected")
    else:
        error("| expected at end of bar")


def meter():
    x = numerator()
    print(f"{x}{token}", end="")
    match("/", "/ expected in meter")
    y = denominator()
    print(y, end="")


def numerator():
    if not token.isdigit():
        error("Expected a number")
    val = ""
    while token.isdigit():
        val += token
        get_token()
    value = int(val)
    if value < 1 or value > 15:
        error("Invalid numerator")
    return value


def denominator():
    if not token.isdigit():
        error("Expected a number")
    val = ""
    while token.isdigit():
        val += token
        get_token()
    value = int(val)
    if value not in (1, 2, 4, 8, 16):
        error("Invalid denominator")
    return value


def chords():
    global parsed_chords
    if token == "N":
        match("N", "N expected")
        match("C", "C expected")
        print("NC", end="")
    elif token == "%":
        match("%", "% expected")
        print("%", end="")
    else:
        while token and token != "|":
            chord()


def chord():
    """chord -> root [description] [bass]"""
    global parsed_chords
    root = read_note()
    qual, ext_type, ext, sus = " ", " ", 0, 0
    bass = ""

    if token in ("-", "+", "o", "^", "s", "n", "(", "5", "6", "7", "9", "1"):
        qual, ext_type, ext, sus = read_description()

    if token == "/":
        match("/", "/ expected")
        bass = read_note()

    parsed_chords.append((root, qual, ext_type, ext, sus, bass))


def read_note():
    global token
    if token not in "ABCDEFG":
        error(f"Invalid note letter {token}")
    note = token
    get_token()
    if token in ("b", "#"):
        note += token
        get_token()
    print(note, end="")
    return note


def read_description():
    global token
    qual, ext_type, ext, sus = " ", " ", 0, 0

    # quality
    if token in ("-", "+", "o"):
        qual = token
        print(token, end="")
        get_token()

    # extensions (^7, 9, 11, 13, etc.)
    if token == "^":
        ext_type = "^"
        print("^", end="")
        get_token()

    if token.isdigit():
        val = ""
        while token.isdigit():
            val += token
            get_token()
        try:
            ext = int(val)
        except ValueError:
            ext = 0
        print(val, end="")

    # parentheses for (9), (13)
    if token == "(":
        match("(", "( expected")
        val = ""
        while token.isdigit():
            val += token
            get_token()
        print(f"({val})", end="")
        match(")", ") expected")

    # omissions (no3 / no5)
    if token == "n":
        match("n", "n expected")
        match("o", "o expected")
        if token == "3":
            print("no3", end="")
            get_token()
        elif token == "5":
            print("no5", end="")
            get_token()
        else:
            error("Invalid omission")

    # suspensions
    if token == "s":
        match("s", "s expected")
        match("u", "u expected")
        match("s", "s expected")
        if token == "2":
            sus = 2
            print("sus2", end="")
            match("2", "2 expected")
        elif token == "4":
            sus = 4
            print("sus4", end="")
            match("4", "4 expected")
        else:
            error("Invalid sus")

    return qual, ext_type, ext, sus


# =====================================================
# === WRAPPER =========================================
# =====================================================
def parse_song(filepath):
    """Wrapper for Full.py integration — returns structured chords."""
    global input_file, parsed_chords
    parsed_chords = []
    with open(filepath, "r") as f:
        input_file = f
        print("The following characters demonstrate the tokens being parsed.\n")
        get_token()
        parse_input()
        print("\nParsing completed successfully\n")
    return parsed_chords


# =====================================================
# === STANDALONE MAIN =================================
# =====================================================
def main():
    filepath = input("Enter the path of the file to be parsed: ").strip()
    if not filepath.lower().endswith(".txt"):
        print("Error: Only .txt files are supported")
        sys.exit(1)
    if not os.path.exists(filepath):
        print("Error: cannot open file")
        sys.exit(1)

    chords = parse_song(filepath)
    print(f"Total parsed chords: {len(chords)}")


if __name__ == "__main__":
    main()


