# Parser Sebas Lopez, Diego Bonilla, Luis Baeza

import sys
import os

# Global variables
token = ''
input_file = None

# -----------------------
# Lexer utilities
# -----------------------
def get_token():
    """Read the next non-whitespace character from the file."""
    global token
    ch = input_file.read(1)
    while ch and ch in (' ', '\n', '\t'):
        ch = input_file.read(1)
    token = ch if ch else ''  # Empty string = EOF


def match(expected, message):
    """Consume a token if it matches the expected character, else raise an error."""
    global token
    if token == expected:
        get_token()
    else:
        error(message)


def error(message):
    print(f"\nParse error: {message}")
    sys.exit(1)

# -----------------------
# Grammar functions
# -----------------------

def parse_input():
    # input -> song EOF
    song()
    if token != '':
        error("EOF expected")


def song():
    # song -> bar {bar} '|'
    # Keep parsing bars until a final '|'
    while token and token != '|':
        bar()
    if token == '|':
        print(token, end='')
        match('|', "| expected")
    else:
        error("| expected at end of song")


def bar():
    # bar -> [meter] chords '|'
    if token.isdigit():
        meter()
    chords()
    if token == '|':
        print(token, end='')
        match('|', "| expected")
    else:
        error("| expected at end of bar")


def meter():
    # meter -> numerator "/" denominator
    x = numerator()
    print(f"{x}{token}", end='')
    match('/', "/ expected in meter")
    y = denominator()
    print(y, end='')


def numerator():
    # numerator -> "1" | "2" | ... | "15"
    if not token.isdigit():
        error("Expected a number")
    value = 0
    while token.isdigit():
        value = value * 10 + int(token)
        get_token()
    if value < 1 or value > 15:
        error("Invalid numerator")
    return value


def denominator():
    # denominator -> "1" | "2" | "4" | "8" | "16"
    if not token.isdigit():
        error("Expected a number")
    value = 0
    while token.isdigit():
        value = value * 10 + int(token)
        get_token()
    if value not in (1, 2, 4, 8, 16):
        error("Invalid denominator")
    return value


def chords():
    # chords -> "NC" | "%" | chord {chord}
    global token
    if token == 'N':
        match('N', "N expected")
        match('C', "C expected")
        print("NC", end='')
    elif token == '%':
        match('%', "% expected")
        print("%", end='')
    else:
        while token and token != '|':
            chord()


def chord():
    # chord -> root [description] [bass]
    root()
    if token in ('s', '-', '+', 'o', '7', '9', '1', '^'):
        description()
    if token == '/':
        bass()


def root():
    # root -> note
    note()


def note():
    # note -> letter [acc]
    letter()
    if token in ('b', '#'):
        acc()


def letter():
    # letter -> A | B | C | D | E | F | G
    global token
    if token in 'ABCDEFG':
        print(token, end='')
        get_token()
    else:
        error("Invalid character found")


def acc():
    # acc -> '#' | 'b'
    global token
    if token in ('#', 'b'):
        print(token, end='')
        get_token()
    else:
        error("Invalid accidental")


def description():
    # description -> qual | qual qnum | qnum | qnum sus | sus
    has_qual = False
    has_qnum = False
    has_sus = False

    if token in ('-', '+', 'o'):
        qual()
        has_qual = True
    if token in ('^', '7', '9', '1'):
        qnum()
        has_qnum = True
    if token == 's' and not has_qual:
        sus()
        has_sus = True
    if not (has_qual or has_qnum or has_sus):
        error("Invalid description: expected qual, qnum, or sus")


def qual():
    # qual -> '-' | '+' | 'o'
    global token
    if token in ('-', '+', 'o'):
        print(token, end='')
        get_token()
    else:
        error("Invalid qual")


def qnum():
    # qnum -> ['^'] num
    global token
    temp = ''
    if token == '^':
        temp = '^'
        match('^', "^ expected")
    x = num()
    print(f"{temp}{x}", end='')


def num():
    # num -> '7' | '9' | '11' | '13'
    global token
    if not token.isdigit():
        error("Expected a number")
    value = 0
    while token.isdigit():
        value = value * 10 + int(token)
        match(token, "")
    if value not in (7, 9, 11, 13):
        error("Invalid num")
    return value


def sus():
    # sus -> 'sus2' | 'sus4'
    global token
    if token == 's':
        match('s', "invalid sus sequence")
        match('u', "invalid sus sequence")
        match('s', "invalid sus sequence")
        if token == '2':
            print("sus2", end='')
            match('2', "2 expected")
        elif token == '4':
            print("sus4", end='')
            match('4', "4 expected")
        else:
            error("Invalid suspended sequence")
    else:
        error("Invalid input as sus")


def bass():
    # bass -> '/' note
    print('/', end='')
    match('/', "/ expected")
    note()


# -----------------------
# Main program
# -----------------------

def main():
    global input_file
    filepath = input("Enter the path of the file to be parsed: ").strip()
    if not filepath.lower().endswith(".txt"):
        print("Error: Only .txt files are supported")
        sys.exit(1)
    if not os.path.exists(filepath):
        print("Error: cannot open file")
        sys.exit(1)

    with open(filepath, 'r') as f:
        input_file = f
        print("The following characters demonstrate the tokens being parsed.\n")
        get_token()
        parse_input()
        print("\n\nParsing completed successfully\n")


if __name__ == "__main__":
    main()
