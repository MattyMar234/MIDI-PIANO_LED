

def note_to_octave(node: int) -> int:
    return node // 12

def octave_note_number(note: int) -> int:
    return note % 12

def white_note_of_octave(note: int) -> int:
    note % 12
    count: int = 0
    
    for i in range(note):
        if not is_altered(i):
            count += 1
            
    return count
    

def is_altered(note: int) -> bool:
    note = note % 12
    return note in [1, 3, 6, 8, 10]

def is_natural(note: int) -> bool:
    return not is_altered(note)

def to_white_note(note: int) -> int:
    if is_altered(note):
        return note - 1
    return note