import re
from collections import Counter

def normalize_note(note):
    """Normalize accidental variants."""
    note = note.replace("\\", "#").replace("Z", "b")
    return note

def parse_chord(token):
    """
    Parse a chord token like A, C#m7, F#7sus4, A(9), B/E, etc.
    Returns the root note only (pitch class).
    """
    # Handle slash chords (take root before /)
    if "/" in token:
        token = token.split("/")[0]

    # Extract root note (A–G with optional # or b)
    match = re.match(r"^([A-Ga-g])([#b-]?)", token.strip())
    if match:
        root = match.group(1).upper() + match.group(2).replace("-", "#")
        return normalize_note(root)
    else:
        raise ValueError(f"Chord root expected, got '{token}'")

def read_song_file(filename):
    """Read chords from a text file separated by | and print as it reads."""
    chords = []
    print("--- Reading song file ---")
    with open(filename, "r") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            print(f"Line {line_num}: {line}")  # live print as it reads
            tokens = line.split("|")
            for token in tokens:
                token = token.strip()
                if not token:
                    continue
                try:
                    chord = parse_chord(token)
                    chords.append(chord)
                except ValueError as e:
                    print(f"Warning: skipping token '{token}' ({e})")
    return chords

def print_histogram(chords):
    """Print and save a histogram of pitch classes."""
    order = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    counter = Counter(chords)
    
    print("\n--- Pitch-Class Histogram ---\n")
    print("\t\t" + "\t".join(f"{i:X}" for i in range(12)))
    print("\t\t" + "\t".join("-" for _ in range(12)))

    lines = []
    for i, note in enumerate(order, start=1):
        marks = []
        for n in order:
            marks.append("*" if n == note else " ")
        line = f"{i:3}. \t" + "\t".join(marks) + f"\t- {note}"
        lines.append(line)
        print(line)

    print("\t\t" + "\t".join("-" for _ in range(12)))
    totals = "\t\t" + "\t".join(str(counter.get(note, 0)).rjust(3) for note in order)
    print(totals)

    # Save to file
    with open("histogram_output.txt", "w") as out:
        out.write("--- Pitch-Class Histogram ---\n\n")
        out.write("\t\t" + "\t".join(f"{i:X}" for i in range(12)) + "\n")
        out.write("\t\t" + "\t".join("-" for _ in range(12)) + "\n")
        for line in lines:
            out.write(line + "\n")
        out.write("\t\t" + "\t".join("-" for _ in range(12)) + "\n")
        out.write(totals + "\n")

    print("\n✅ Histogram saved as 'histogram_output.txt'")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python fulltest_fixed.py <song_file.txt>")
        sys.exit(1)
    filename = sys.argv[1]
    chords = read_song_file(filename)
    print_histogram(chords)

