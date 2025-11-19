# =====================================================
# === Full Parser + Calculator (Final Integration) ====
# =====================================================
# Authors: Sebastián López, Diego Bonilla, Luis Baeza
# =====================================================

import os
import sys

from Parser import parse_song  


# =====================================================
# === DATA STRUCTURES =================================
# =====================================================

class Chord:
    def __init__(self):
        self.root = ""
        self.qual = " "
        self.ext_type = " "
        self.extension = 0
        self.sus = 0
        self.bass = ""
        self.omit3 = False
        self.omit5 = False


class ChordNode:
    def __init__(self, chord):
        self.chord = chord
        self.next = None


def append_chord(head, chord):
    node = ChordNode(chord)
    if head is None:
        return node
    t = head
    while t.next:
        t = t.next
    t.next = node
    return head


# =====================================================
# === NOTE → PITCH CLASS ==============================
# =====================================================

def note_to_pitch_class(note):
    """
    Map a note like C, C#, Db, etc. to a pitch class 0..11.
    C=0, C#=1, D=2, ..., B=11.
    """
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
# === CHORD → PITCH-CLASS ARRAY =======================
# =====================================================

def create_chord_arr(chord):
    """
    Given a Chord object, return a 12-element 0/1 array representing
    which pitch classes are present (C..B).
    Matches the expected histograms.
    """

    # No chord: if we ever had "NC" chords, they would be skipped in Parser,
    # so we should not see them here. But we guard anyway.
    if chord.root == "" or chord.root == "NC":
        return [0] * 12

    arr = [0] * 12

    root_pc = note_to_pitch_class(chord.root)
    if root_pc == -1:
        return arr

    # Always include the root
    arr[root_pc] = 1

    # Basic triad intervals
    third_maj = (root_pc + 4) % 12
    third_min = (root_pc + 3) % 12
    fifth = (root_pc + 7) % 12

    # ===== QUALITY =====
    if chord.qual == "-":      # minor
        arr[third_min] = 1
        arr[fifth] = 1
    elif chord.qual == "+":    # augmented
        arr[third_maj] = 1
        arr[(root_pc + 8) % 12] = 1
    elif chord.qual == "o":    # diminished
        arr[third_min] = 1
        arr[(root_pc + 6) % 12] = 1
    else:                      # default major triad
        arr[third_maj] = 1
        arr[fifth] = 1

    # ===== OMISSIONS (no3 / no5) =====
    if chord.omit3:
        arr[third_maj] = 0
        arr[third_min] = 0
    if chord.omit5:
        arr[fifth] = 0

    # ===== EXTENSIONS (allow list/tuple) =====
    exts = chord.extension
    if not isinstance(exts, (list, tuple)):
        exts = [exts]

    # Power chord: X5 → only root + fifth, no third
    if 5 in exts and chord.qual.strip() == "":
        arr = [0] * 12
        arr[root_pc] = 1
        arr[fifth] = 1
        return arr

    # 6th (or 1 treated as 6)
    if any(e in (1, 6) for e in exts):
        arr[(root_pc + 9) % 12] = 1  # 13th/6th

    # 7th (dominant vs. major 7th)
    if 7 in exts:
        if chord.ext_type == "^":
            arr[(root_pc + 11) % 12] = 1  # maj7
        else:
            arr[(root_pc + 10) % 12] = 1  # b7

    # 9th
    if 9 in exts:
        arr[(root_pc + 2) % 12] = 1

    # 11th
    if 11 in exts:
        arr[(root_pc + 5) % 12] = 1

    # 13th
    if 13 in exts:
        arr[(root_pc + 9) % 12] = 1

    # ===== SUSPENSIONS =====
    if chord.sus == 2:
        arr[third_maj] = 0
        arr[third_min] = 0
        arr[(root_pc + 2) % 12] = 1
    elif chord.sus == 4:
        arr[third_maj] = 0
        arr[third_min] = 0
        arr[(root_pc + 5) % 12] = 1

    # ===== SLASH BASS =====
    if chord.bass:
        bpc = note_to_pitch_class(chord.bass)
        if bpc != -1:
            arr[bpc] = 1

    return arr


# =====================================================
# === PRINT CHORD (RIGHT-SIDE LABEL) ==================
# =====================================================

def print_chord(ch):
    out = ch.root
    if ch.qual.strip():
        out += ch.qual

    if ch.ext_type == "^":
        out += f"^{ch.extension}"
    elif ch.extension:
        if ch.extension in (9, 11, 13):
            out += f"({ch.extension})"
        else:
            out += str(ch.extension)

    if ch.sus:
        out += f"sus{ch.sus}"

    if ch.bass:
        out += f"/{ch.bass}"

    print(out, end='')


# =====================================================
# === PRINT HISTOGRAM =================================
# =====================================================

def print_chords(head):
    t = head
    totals = [0] * 12
    n = 1

    print("\n")
    header = "\t".join(["", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B"])
    print("     \t" + header)
    print("     \t" + "\t".join(["-"] * 12))

    while t:
        arr = create_chord_arr(t.chord)
        print(f"{n:4d}. ", end="\t")
        for i in range(12):
            if arr[i]:
                print(" * ", end="\t")
                totals[i] += 1
            else:
                print("   ", end="\t")
        print("- ", end="")
        print_chord(t.chord)
        print()
        t = t.next
        n += 1

    print("     \t" + "\t".join(["-"] * 12))
    print("     \t" + "\t".join(f"{x:3d}" for x in totals))
    print()


# =====================================================
# === MAIN ============================================
# =====================================================

def main():
    # Allow either: python full.py <file>  OR  interactive input
    if len(sys.argv) == 2:
        filepath = sys.argv[1]
    else:
        filepath = input("Enter the path of the file to be parsed: ").strip()

    if not filepath.lower().endswith(".txt"):
        print("Error: Only .txt files are supported.")
        sys.exit(1)
    if not os.path.exists(filepath):
        print("Error: Cannot open file.")
        sys.exit(1)

    # --- Parse chords using Parser.py ---
    chords = parse_song(filepath)
    if not chords:
        print("\n(No chords were parsed — check input file.)")
        sys.exit(1)

    # --- Build linked list of Chord objects ---
    head = None
    for root, qual, ext_type, extension, sus, bass, omit3, omit5 in chords:
        c = Chord()
        c.root = root
        c.qual = qual
        c.ext_type = ext_type
        c.extension = extension
        c.sus = sus
        c.bass = bass
        c.omit3 = omit3
        c.omit5 = omit5
        head = append_chord(head, c)

    # --- Print histogram to stdout ---
    print("\n--- Pitch-Class Histogram ---")
    print_chords(head)

    # --- Save histogram to file ---
    outname = os.path.splitext(os.path.basename(filepath))[0] + "_output.txt"
    with open(outname, "w") as out:
        backup = sys.stdout
        sys.stdout = out
        print("--- Pitch-Class Histogram ---")
        print_chords(head)
        print("Parsing and calculation completed successfully.")
        sys.stdout = backup

    print(f"\nHistogram saved to '{outname}'\n")
    print("Parsing and calculation completed successfully.\n")


if __name__ == "__main__":
    main()
