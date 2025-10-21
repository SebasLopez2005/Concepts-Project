# =====================================================
# === Standalone Chord Calculator / Histogram Test ====
# =====================================================
# Authors: Sebastián López, Diego Bonilla, Luis Baeza
# =====================================================

import sys

# =====================================================
# === CHORD DATA STRUCTURES ===========================
# =====================================================
class Chord:
    def __init__(self, root="", qual=" ", ext_type=" ", extension=0, sus=0, bass=""):
        self.root = root
        self.qual = qual
        self.ext_type = ext_type
        self.extension = extension
        self.sus = sus
        self.bass = bass


class ChordNode:
    def __init__(self, chord):
        self.chord = chord
        self.next = None


# =====================================================
# === LINKED LIST HELPERS =============================
# =====================================================
def append_chord(head, chord):
    node = ChordNode(chord)
    if head is None:
        return node
    temp = head
    while temp.next:
        temp = temp.next
    temp.next = node
    return head


# =====================================================
# === NOTE TO PITCH CLASS =============================
# =====================================================
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


# =====================================================
# === CHORD TO PITCH ARRAY ============================
# =====================================================
def create_chord_arr(chord):
    """Pitch class generator (matches full.py histogram logic)."""
    arr = [0] * 12
    root_pc = note_to_pitch_class(chord.root)
    if root_pc == -1:
        print(f"Invalid note: {chord.root}")
        sys.exit(1)
    arr[root_pc] = 1

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

    # --- Special: A1 (or any X1) means only root note ---
    if 1 in extensions and chord.qual.strip() == "" and not chord.sus:
        arr = [0] * 12
        arr[root_pc] = 1

    return arr


# =====================================================
# === PRINT HELPERS ==================================
# =====================================================
def print_chord(chord):

    out = chord.root
    if chord.qual.strip():
        out += chord.qual
    if chord.ext_type == "^":
        out += f"{chord.ext_type}{chord.extension}"
    elif chord.extension:
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
# === MAIN TEST (Hardcoded Input) =====================
# =====================================================
def main():
    # Example chord list to test histogram logic
    chord_list = [
        ("E", " ", " ", 5, 0, ""),      # E5
        ("B", " ", " ", 0, 0, ""),      # B
        ("C#", "-", " ", 7, 0, ""),     # C#-7
        ("A", " ", " ", 9, 0, ""),      # A(9)
        ("E", " ", " ", 0, 0, ""),      # E
        ("B", " ", " ", 0, 0, ""),      # B
        ("G#", "-", " ", 7, 0, ""),     # G#-7
        ("A", " ", " ", 6, 0, ""),      # A6
        ("B", " ", " ", 0, 0, "A"),     # B/A
        ("E", " ", " ", 0, 2, ""),      # Esus2
        ("A", " ", " ", [6, 9], 0, ""), # A6(9)
    ]

    head = None
    for root, qual, ext_type, ext, sus, bass in chord_list:
        c = Chord(root, qual, ext_type, ext, sus, bass)
        head = append_chord(head, c)

    print("\n--- Pitch-Class Histogram (Test Mode) ---")
    print_chords(head)
    print("Parsing and calculation completed successfully.\n")


if __name__ == "__main__":
    main()
