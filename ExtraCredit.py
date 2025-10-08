import os
import sys
from enum import Enum, auto

# -----------------------------
# Enumerations for chord parts
# -----------------------------
class Quality(Enum):
    MAJOR = auto()
    MINOR = auto()
    AUG = auto()
    DIM = auto()
    POW = auto()
    UNISON = auto()


class Extension(Enum):
    NONE = auto()
    SIX = auto()
    SEV = auto()
    SSEV = auto()
    NIN = auto()
    SNIN = auto()
    ELE = auto()
    SELE = auto()
    THR = auto()
    STHR = auto()


class Suspension(Enum):
    NONE = auto()
    SUS2 = auto()
    SUS4 = auto()
    SUS24 = auto()


class Omission(Enum):
    NONE = auto()
    NO3 = auto()
    NO5 = auto()
    NO35 = auto()


# -----------------------------
# Data classes
# -----------------------------
class Note:
    def __init__(self, letter='', accidental=''):
        self.letter = letter
        self.accidental = accidental


class AddInfo:
    def __init__(self, accid='', add_type=None):
        self.accid = accid
        self.add_type = add_type  # 5, 9, 11, 13, etc.


class Chord:
    def __init__(self):
        self.root = Note()
        self.qual = Quality.MAJOR
        self.qnum = Extension.NONE
        self.add = AddInfo()
        self.sus = Suspension.NONE
        self.om = Omission.NONE
        self.bass = Note()


class ChordNode:
    def __init__(self, chord):
        self.chord = chord
        self.next = None


# -----------------------------
# Lexer utilities
# -----------------------------
class Lexer:
    def __init__(self, filepath):
        if not filepath.lower().endswith(".txt"):
            raise ValueError("Error: Only .txt files are supported")
        self.file = open(filepath, "r")
        self.token = ''
        self.get_token()

    def get_token(self):
        """Get next non-whitespace character."""
        ch = self.file.read(1)
        while ch and ch in (' ', '\n', '\t'):
            ch = self.file.read(1)
        self.token = ch if ch else ''

    def match(self, expected):
        """Consume token if it matches."""
        if self.token == expected:
            self.get_token()
        elif self.token == '':
            raise SyntaxError("Unexpected end of input")
        else:
            raise SyntaxError(f"Unexpected character: '{self.token}'")

    def close(self):
        self.file.close()


# -----------------------------
# Parser class
# -----------------------------
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

    def error(self, msg):
        print(f"Parse error: {msg}")
        sys.exit(1)

    # === Grammar entry ===
    def parse_input(self):
        head = None
        head = self.song(head)
        if self.lexer.token != '':
            self.error("EOF expected")
        print("\nParsing completed successfully.\n")
        self.print_chords(head)
        self.free_chords(head)

    # === Grammar productions ===
    def song(self, head):
        while self.lexer.token and self.lexer.token != '|':
            head = self.bar(head)
        if self.lexer.token == '|':
            self.lexer.match('|')
        return head

    def bar(self, head):
        if self.lexer.token.isdigit():
            self.meter()
        head = self.chords(head)
        if self.lexer.token == '|':
            self.lexer.match('|')
        return head

    def meter(self):
        self.numerator()
        self.lexer.match('/')
        self.denominator()

    def numerator(self):
        val = 0
        if not self.lexer.token.isdigit():
            self.error("Expected number")
        while self.lexer.token.isdigit():
            val = val * 10 + int(self.lexer.token)
            self.lexer.get_token()
        if val < 1 or val > 15:
            self.error("Invalid numerator")
        return val

    def denominator(self):
        val = 0
        if not self.lexer.token.isdigit():
            self.error("Expected number")
        while self.lexer.token.isdigit():
            val = val * 10 + int(self.lexer.token)
            self.lexer.get_token()
        if val not in (1, 2, 4, 8, 16):
            self.error("Invalid denominator")
        return val

    def chords(self, head):
        if self.lexer.token == 'N':
            self.lexer.match('N')
            self.lexer.match('C')
        elif self.lexer.token == '%':
            self.lexer.match('%')
        else:
            while self.lexer.token not in ('|', ''):
                new_chord = self.chord()
                head = self.append_chord(head, new_chord)
        return head

    def chord(self):
        chord = Chord()
        chord.root = self.note()
        if self.lexer.token in "-+o51679^#b(":
            self.description(chord)
        if self.lexer.token == '/':
            self.lexer.match('/')
            chord.bass = self.note()
        return chord

    def note(self):
        letter = self.letter()
        accidental = ''
        if self.lexer.token in ('b', '#'):
            accidental = self.acc()
        return Note(letter, accidental)

    def letter(self):
        if self.lexer.token in "ABCDEFG":
            temp = self.lexer.token
            self.lexer.get_token()
            return temp
        self.error("Invalid letter found")

    def acc(self):
        if self.lexer.token in "#b":
            temp = self.lexer.token
            self.lexer.get_token()
            return temp
        self.error("Invalid accidental")

    def description(self, chord):
        has_any = False
        if self.lexer.token in "-o51":
            chord.qual = self.qual()
            has_any = True
        if self.lexer.token in "^67891":
            chord.qnum = self.qnum()
            has_any = True
        if self.lexer.token in "#b(":
            self.add(chord)
            has_any = True
        if self.lexer.token == 's':
            chord.sus = self.sus()
            has_any = True
        if self.lexer.token == 'n':
            chord.om = self.omit()
            has_any = True

        if not has_any:
            self.error("Expected at least one description")

    def qual(self):
        t = self.lexer.token
        if t == '-':
            self.lexer.match('-')
            return Quality.MINOR
        elif t == '+':
            self.lexer.match('+')
            return Quality.AUG
        elif t == 'o':
            self.lexer.match('o')
            return Quality.DIM
        elif t == '5':
            self.lexer.match('5')
            return Quality.POW
        elif t == '1':
            self.lexer.match('1')
            return Quality.UNISON
        else:
            self.error("Invalid quality")

    def qnum(self):
        t = self.lexer.token
        major = False
        if t == '^':
            major = True
            self.lexer.match('^')
            t = self.lexer.token

        mapping = {
            '6': Extension.SIX,
            '7': Extension.SSEV if major else Extension.SEV,
            '9': Extension.SNIN if major else Extension.NIN,
        }

        if t in mapping:
            self.lexer.get_token()
            return mapping[t]

        if t == '1':
            self.lexer.get_token()
            if self.lexer.token == '1':
                self.lexer.get_token()
                return Extension.SELE if major else Extension.ELE
            elif self.lexer.token == '3':
                self.lexer.get_token()
                return Extension.STHR if major else Extension.THR
            else:
                self.error("Expected 1 or 3 after 1")

        self.error("Invalid extended type")

    def add(self, chord):
        # add -> alt | ( alt )
        if self.lexer.token == '(':
            self.lexer.match('(')
            self.alt(chord)
            if self.lexer.token == ')':
                self.lexer.match(')')
        else:
            self.alt(chord)

    def alt(self, chord):
        accid = ''
        if self.lexer.token in ('#', 'b'):
            accid = self.lexer.token
            self.lexer.get_token()
        if self.lexer.token in '59113':
            add_type = ''
            while self.lexer.token.isdigit():
                add_type += self.lexer.token
                self.lexer.get_token()
            chord.add = AddInfo(accid, int(add_type))
        else:
            self.error("Invalid alteration in add clause")

    def sus(self):
        self.lexer.match('s')
        self.lexer.match('u')
        self.lexer.match('s')
        result = None
        if self.lexer.token == '2':
            self.lexer.match('2')
            result = Suspension.SUS2
        elif self.lexer.token == '4':
            self.lexer.match('4')
            result = Suspension.SUS4
        else:
            self.error("Invalid sus value")

        # check for combined sus24
        if result == Suspension.SUS2 and self.lexer.token == '4':
            self.lexer.match('4')
            result = Suspension.SUS24
        return result

    def omit(self):
        if self.lexer.token == 'n':
            self.lexer.match('n')
            if self.lexer.token == 'o':
                self.lexer.match('o')
                if self.lexer.token == '3':
                    self.lexer.match('3')
                    if self.lexer.token == '5':
                        self.lexer.match('5')
                        return Omission.NO35
                    return Omission.NO3
                elif self.lexer.token == '5':
                    self.lexer.match('5')
                    return Omission.NO5
        self.error("Invalid omission type")

    # -----------------------------
    # Linked list utilities
    # -----------------------------
    def append_chord(self, head, chord):
        node = ChordNode(chord)
        if head is None:
            return node
        temp = head
        while temp.next:
            temp = temp.next
        temp.next = node
        return head

    def free_chords(self, head):
        head = None

    def print_chords(self, head):
        temp = head
        while temp:
            self.print_chord(temp.chord)
            temp = temp.next

    def print_chord(self, chord):
        s = f"Chord: Root {chord.root.letter}{chord.root.accidental or ''}, "
        s += f"Quality {chord.qual.name}, "
        s += f"Omission {chord.om.name}, "
        s += f"Suspension {chord.sus.name}\n"
        print(s)


# -----------------------------
# Main entry
# -----------------------------
def main():
    filepath = input("Enter the path of the file to be parsed: ").strip()
    try:
        lexer = Lexer(filepath)
        parser = Parser(lexer)
        parser.parse_input()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            lexer.close()
        except:
            pass


if __name__ == "__main__":
    main()
