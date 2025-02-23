

def note_octave(node: int) -> int:
    return node // 12


def octave_note(note: int) -> int:
    return note % 12

def is_altered(note: int) -> bool:
    return note in [1, 3, 6, 8, 10]

def is_natural(note: int) -> bool:
    return not is_altered(note)

def to_white_note(note: int) -> int:
    if is_altered(note):
        return note - 1
    return note