# =====================================================
# === Full Chord Parser + Calculator (Extra Credit) ===
# =====================================================
# Authors: Sebastián López, Diego Bonilla, Luis Baeza
# =====================================================

import os
import sys

# =====================================================
# === GLOBALS =========================================
# =====================================================
token = ""
input_file = None
parsed_chords = []  # [(root, qual, ext, ext_type, sus, bass)]


# =====================================================
# === ERROR & TOKEN HANDLING ==========================
# =====================================================
def error(message):
    print(f"\nParse error: {message}")
    sys.exit(1)


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


# =====================================================
# === PARSER GRAMMAR =================================
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

    parsed_chords.append((root, qual, ext, ext_type, sus, bass))


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

    # parentheses for (9) (13)
    if token == "(":
        match("(", "( expected")
        val = ""
        while token.isdigit():
            val += token
            get_token()
        try:
            paren_ext = int(val)
        except ValueError:
            paren_ext = 0
        print(f"({val})", end="")
        match(")", ") expected")
        # ✅ store the parenthesis extension — override or add
        # Combine if both exist (like A6(9))
        if ext and paren_ext and ext != paren_ext:
            ext = (ext, paren_ext)
        else:
            ext = paren_ext if ext == 0 else ext


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
# === PARSER WRAPPER =================================
# =====================================================
def parse_song(filepath):
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
# === CALCULATOR / HARMONIC ANALYSIS =================
# =====================================================
class Chord:
    def __init__(self):
        self.root = ""
        self.qual = " "
        self.extension = 0
        self.ext_type = " "
        self.sus = 0
        self.bass = ""


class ChordNode:
    def __init__(self, chord):
        self.chord = chord
        self.next = None


def append_chord(head, chord):
    node = ChordNode(chord)
    if head is None:
        return node
    temp = head
    while temp.next:
        temp = temp.next
    temp.next = node
    return head


def note_to_pitch_class(note):
    if not note:
        return -1
    base = note[0]
    acc = note[1] if len(note) > 1 else ""
    mapping = {
        "C": {"": 0, "#": 1, "b": 11},
        "D": {"": 2, "#": 3, "b": 1},
        "E": {"": 4, "#": 5, "b": 3},
        "F": {"": 5, "#": 6, "b": 4},
        "G": {"": 7, "#": 8, "b": 6},
        "A": {"": 9, "#": 10, "b": 8},
        "B": {"": 11, "#": 0, "b": 10},
    }
    return mapping.get(base, {}).get(acc, -1)


def create_chord_arr(chord):
    """Final locked-in pitch class generator (matches expected histogram, supports multi-extensions like A6(9))."""
    arr = [0] * 12
    root_pc = note_to_pitch_class(chord.root)
    if root_pc == -1:
        print(f"Invalid note: {chord.root}")
        sys.exit(1)
    arr[root_pc] = 1

    # Common intervals
    third_major = (root_pc + 4) % 12
    third_minor = (root_pc + 3) % 12
    fifth = (root_pc + 7) % 12

    # --- Quality ---
    if chord.qual == "-":         # minor
        arr[third_minor] = 1
        arr[fifth] = 1
    elif chord.qual == "+":       # augmented
        arr[third_major] = 1
        arr[(root_pc + 8) % 12] = 1
    elif chord.qual == "o":       # diminished
        arr[third_minor] = 1
        arr[(root_pc + 6) % 12] = 1
    else:                         # major
        arr[third_major] = 1
        arr[fifth] = 1

    # ✅ Allow multiple extensions (tuple or list)
    extensions = chord.extension if isinstance(chord.extension, (list, tuple)) else [chord.extension]

    # --- Power chord (5): root + fifth only ---
    if 5 in extensions and chord.qual.strip() == "":
        arr = [0] * 12
        arr[root_pc] = 1
        arr[fifth] = 1
        return arr

    # --- Add 6th (or 1 treated as 6) ---
    if any(e in (1, 6) for e in extensions):
        arr[(root_pc + 9) % 12] = 1

    # --- Seventh chords ---
    if 7 in extensions:
        arr[(root_pc + (11 if chord.ext_type == "^" else 10)) % 12] = 1
    # --- Ninth chords ---
    if 9 in extensions:
        arr[(root_pc + 2) % 12] = 1
    # --- Eleventh chords ---
    if 11 in extensions:
        arr[(root_pc + 5) % 12] = 1
    # --- Thirteenth chords ---
    if 13 in extensions:
        arr[(root_pc + 9) % 12] = 1

    # --- Suspensions ---
    if chord.sus == 2:
        arr[third_major] = 0
        arr[third_minor] = 0
        arr[(root_pc + 2) % 12] = 1
    elif chord.sus == 4:
        arr[third_major] = 0
        arr[third_minor] = 0
        arr[(root_pc + 5) % 12] = 1

    # --- Slash chords (bass note) ---
    if chord.bass:
        bpc = note_to_pitch_class(chord.bass)
        if bpc != -1:
            arr[bpc] = 1

    # --- Special: A1 (or any X1) means only root note (avoid extra tones) ---
    if 1 in extensions and chord.qual.strip() == "" and not chord.sus:
        arr = [0] * 12
        arr[root_pc] = 1

    return arr


def print_chord(chord):

    out = chord.root
    if chord.qual.strip():
        out += chord.qual

    if chord.ext_type == "^":
        out += f"{chord.ext_type}{chord.extension}"
    elif chord.extension:
        if chord.extension in (9, 11, 13):
            out += f"({chord.extension})"
        else:
            out += str(chord.extension)


    if chord.sus:
        out += f"sus{chord.sus}"
    if chord.bass:
        out += f"/{chord.bass}"

    print(out, end='')


def print_chords(head):
    temp = head
    totals = [0] * 12
    chord_num = 1

    print("\n")
    header = "\t".join(["", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B"])
    print("     \t" + header)
    print("     \t" + "\t".join(["-"] * 12))

    while temp:
        arr = create_chord_arr(temp.chord)
        print(f"{chord_num:4d}. ", end="\t")
        for i in range(12):
            if arr[i]:
                print(" * ", end="\t")
                totals[i] += 1
            else:
                print("   ", end="\t")
        print("- ", end="")
        print_chord(temp.chord)
        print()
        temp = temp.next
        chord_num += 1

    print("     \t" + "\t".join(["-"] * 12))
    print("     \t" + "\t".join(f"{x:3d}" for x in totals))
    print()


# =====================================================
# === MAIN ============================================
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
    if not chords:
        print("\n(No chords were parsed — check input file.)")
        sys.exit(1)

    head = None
    for root, qual, ext, ext_type, sus, bass in chords:
        c = Chord()
        c.root, c.qual, c.extension, c.ext_type, c.sus, c.bass = (
            root, qual, ext, ext_type, sus, bass
        )
        head = append_chord(head, c)

    print("\n--- Pitch-Class Histogram ---")
    print_chords(head)

    output_filename = os.path.splitext(os.path.basename(filepath))[0] + "_output.txt"
    with open(output_filename, "w") as out:
        sys_stdout_backup = sys.stdout
        sys.stdout = out
        print("--- Pitch-Class Histogram ---")
        print_chords(head)
        print("Parsing and calculation completed successfully.")
        sys.stdout = sys_stdout_backup

    print(f"\nHistogram saved to '{output_filename}'\n")
    print("Parsing and calculation completed successfully.\n")


if __name__ == "__main__":
    main()


