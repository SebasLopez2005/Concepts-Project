import os
import sys

# -------------------------------
# Data structures
# -------------------------------
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


# -------------------------------
# Linked-list helpers
# -------------------------------
def create_node(chord):
    return ChordNode(chord)


def append_chord(head, chord):
    new_node = create_node(chord)
    if head is None:
        return new_node
    temp = head
    while temp.next is not None:
        temp = temp.next
    temp.next = new_node
    return head


def free_chords(head):
    # No manual free in Python, but for symmetry:
    head = None


# -------------------------------
# Pitch-class calculations
# -------------------------------
def note_to_pitch_class(note):
    """Convert note name (e.g. 'Db', 'F#', 'A') to pitch class 0–11."""
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
    """Create a 12-element array representing the chord's pitch classes."""
    arr = [0] * 12
    root_pc = note_to_pitch_class(chord.root)
    if root_pc == -1:
        print(f"Invalid note: {chord.root}")
        sys.exit(1)

    arr[root_pc] = 1  # Root always present

    # --- Chord quality ---
    if chord.qual == "-":  # Minor
        arr[(root_pc + 3) % 12] = 1
        arr[(root_pc + 7) % 12] = 1
    elif chord.qual == "+":  # Augmented
        arr[(root_pc + 4) % 12] = 1
        arr[(root_pc + 8) % 12] = 1
    elif chord.qual == "o":  # Diminished
        arr[(root_pc + 3) % 12] = 1
        arr[(root_pc + 6) % 12] = 1
    else:  # Major or default
        arr[(root_pc + 4) % 12] = 1
        arr[(root_pc + 7) % 12] = 1

    # --- Extensions ---
    ext = chord.extension
    if ext == 7:
        arr[(root_pc + (11 if chord.ext_type == "^" else 10)) % 12] = 1
    elif ext == 9:
        arr[(root_pc + 2) % 12] = 1
        arr[(root_pc + (11 if chord.ext_type == "^" else 10)) % 12] = 1
    elif ext == 11:
        arr[(root_pc + 5) % 12] = 1
        arr[(root_pc + (11 if chord.ext_type == "^" else 10)) % 12] = 1
    elif ext == 13:
        arr[(root_pc + 9) % 12] = 1
        arr[(root_pc + (11 if chord.ext_type == "^" else 10)) % 12] = 1

    # --- Suspensions ---
    if chord.sus == 2:
        arr[(root_pc + 2) % 12] = 1
        arr[(root_pc + 4) % 12] = 0
        arr[(root_pc + 7) % 12] = 1
    elif chord.sus == 4:
        arr[(root_pc + 5) % 12] = 1
        arr[(root_pc + 4) % 12] = 0
        arr[(root_pc + 7) % 12] = 1

    # --- Bass ---
    if chord.bass:
        bass_pc = note_to_pitch_class(chord.bass)
        if bass_pc != -1:
            arr[bass_pc] = 1

    return arr


def print_chord(chord):
    """Print chord in human-readable format (e.g. F-7sus4/Bb)."""
    out = chord.root
    if chord.qual != " ":
        out += chord.qual
    if chord.ext_type == "^":
        out += f"{chord.ext_type}{chord.extension}"
    elif chord.extension != 0:
        out += str(chord.extension)
    if chord.sus != 0:
        out += f"sus{chord.sus}"
    if chord.bass:
        out += f"/{chord.bass}"
    print(out, end='')


def print_chords(head):
    """Print all chords and histogram of total pitch classes."""
    temp = head
    chord_num = 1
    totals = [0] * 12

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


# -------------------------------
# Parser functions (simplified)
# -------------------------------
def error(msg):
    print(f"Parse error: {msg}")
    sys.exit(1)


def get_token(f):
    """Generator for tokens: yields one char at a time skipping whitespace."""
    while True:
        ch = f.read(1)
        if not ch:
            yield ''  # EOF
            break
        if ch not in (' ', '\t', '\n'):
            yield ch


# -------------------------------
# Main program logic
# -------------------------------
def main():
    filepath = input("Enter the path of the file to be parsed: ").strip()
    if not filepath.lower().endswith(".txt"):
        print("Error: Only .txt files are supported")
        sys.exit(1)
    if not os.path.exists(filepath):
        print("Error: cannot open file")
        sys.exit(1)

    # Build chord list manually (here, simplified)
    # You can plug in your parser from before to fill this list.
    # Example placeholder for demo purposes:
    example_chords = [
        ("F", "-", 0, " ", 0, ""),
        ("Bb", " ", 7, " ", 0, ""),
        ("Eb", " ", 7, " ", 4, ""),  # Eb7sus4
    ]

    head = None
    for root, qual, ext, ext_type, sus, bass in example_chords:
        c = Chord()
        c.root = root
        c.qual = qual
        c.extension = ext
        c.ext_type = ext_type
        c.sus = sus
        c.bass = bass
        head = append_chord(head, c)

    print_chords(head)
    print("\nParsing completed successfully.")


if __name__ == "__main__":
    main()
