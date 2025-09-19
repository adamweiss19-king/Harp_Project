# A Major Harmonica (Standard Richter Tuning)
# The notes available on a standard 10-hole diatonic harmonica in the key of A.
a_major_harmonica = {
    # Blow notes
    '1': 'A4', '2': 'C#5', '3': 'E5', '4': 'A5', '5': 'C#6', '6': 'E6', '7': 'A6', '8': 'C#7', '9': 'E7', '10': 'A7',
    
    # Draw notes
    '-1': 'B4', '-2': 'E5', '-3': 'G#5', '-4': 'B5', '-5': 'D6', '-6': 'F#6', '-7': 'B6', '-8': 'D7', '-9': 'F#7', '-10': 'B7',
    
    # Overblows (on holes 1-6, raising the pitch)
    '1o': 'Bb4', '4o': 'Bb5', '5o': 'D#6', '6o': 'F#6', 
    
    # Blow Bends (on holes 7-10, lowering the pitch)
    '7b': 'G#6', '8b': 'C7', '9b': 'D#7', '10b': 'G#7',
    
    # Draw Bends
    '-1b': 'A#4', '-1bb': 'A4',
    '-2b': 'D#5', '-2bb': 'C#5', '-2bbb': 'C5',
    '-3b': 'F#5', '-3bb': 'F5', '-3bbb': 'E5',
    '-4b': 'A#5',
    '-6b': 'E6',
}

# c_natural_minor_harmonica
# A harmonica specifically tuned to the C natural minor scale.
c_natural_minor_harmonica = {
    # Blow notes
    '1': 'C4', '2': 'Eb4', '3': 'G4', '4': 'C5', '5': 'Eb5', '6': 'G5', '7': 'C6', '8': 'Eb6', '9': 'G6', '10': 'C7',
    
    # Draw notes
    '-1': 'D4', '-2': 'F4', '-3': 'Ab4', '-4': 'Bb4', '-5': 'Db5', '-6': 'F5', '-7': 'Ab5', '-8': 'Bb5', '-9': 'Db6', '-10': 'F6',

    # Overblows (on holes 1-6, raising the pitch)
    '1o': 'C#4', '4o': 'C#5', 
    
    # Blow Bends (on holes 7-10, lowering the pitch)
    '7b': 'B5', '8b': 'D#6', '9b': 'Gb6', '10b': 'B6',

    # Draw Bends
    '-1b': 'C#4',
    '-2b': 'E4', '-2bb': 'Eb4',
    '-3b': 'G4', '-3bb': 'Gb4',
    '-4b': 'A4', '-4bb': 'Ab4',
    '-5b': 'C5', '-5bb': 'B4',
    '-6b': 'E5',
    '-7b': 'G5', '-7bb': 'Gb5',
    '-8b': 'A5', '-8bb': 'Ab5',
    '-9b': 'C6', '-9bb': 'B5',
    '-10b': 'E6',
}

# d_natural_minor_harmonica
# A harmonica specifically tuned to the D natural minor scale.
d_natural_minor_harmonica = {
    # Blow notes
    '1': 'D4', '2': 'F4', '3': 'A4', '4': 'D5', '5': 'F5', '6': 'A5', '7': 'D6', '8': 'F6', '9': 'A6', '10': 'D7',
    
    # Draw notes
    '-1': 'E4', '-2': 'G4', '-3': 'Bb4', '-4': 'C5', '-5': 'Eb5', '-6': 'G5', '-7': 'Bb5', '-8': 'C6', '-9': 'Eb6', '-10': 'G6',

    # Overblows (on holes 1-6, raising the pitch)
    '1o': 'Eb4', '4o': 'Eb5',
    
    # Blow Bends (on holes 7-10, lowering the pitch)
    '7b': 'C#6', '8b': 'E6', '9b': 'Ab6', '10b': 'C#7',
    
    # Draw Bends
    '-1b': 'Eb4',
    '-2b': 'F#4', '-2bb': 'F4',
    '-3b': 'A4', '-3bb': 'Ab4',
    '-4b': 'B4', '-4bb': 'Bb4',
    '-5b': 'D5', '-5bb': 'Db5',
    '-6b': 'F#5',
    '-7b': 'A5', '-7bb': 'Ab5',
    '-8b': 'B5', '-8bb': 'Bb5',
    '-9b': 'D6', '-9bb': 'Db6',
    '-10b': 'F#6',
}

# Example of how you would use these dictionaries
def get_note_from_tab(harmonica_dict, tab):
    """
    Looks up a harmonica tab in a given dictionary and returns the note.
    """
    # Ensure the lookup key is a string for a proper dictionary lookup
    tab_str = str(tab)
    if tab_str in harmonica_dict:
        return harmonica_dict[tab_str]
    else:
        return "Tab not found"

# Let's try to interpret some tabs with the new, correct notation
print("A Major Harmonica:")
print(f"Tab '4' is the note: {get_note_from_tab(a_major_harmonica, '4')}")
print(f"Tab '-3bb' is the note: {get_note_from_tab(a_major_harmonica, '-3bb')}")
print(f"Tab '1o' (overblow) is the note: {get_note_from_tab(a_major_harmonica, '1o')}")
print(f"Tab '8b' (blow bend) is the note: {get_note_from_tab(a_major_harmonica, '8b')}")

print("\nC Natural Minor Harmonica:")
print(f"Tab '3' is the note: {get_note_from_tab(c_natural_minor_harmonica, '3')}")
print(f"Tab '-3' is the note: {get_note_from_tab(c_natural_minor_harmonica, '-3')}")
print(f"Tab '4o' (overblow) is the note: {get_note_from_tab(c_natural_minor_harmonica, '4o')}")
print(f"Tab '9b' (blow bend) is the note: {get_note_from_tab(c_natural_minor_harmonica, '9b')}")

print("\nD Natural Minor Harmonica:")
print(f"Tab '1' is the note: {get_note_from_tab(d_natural_minor_harmonica, '1')}")
print(f"Tab '-5' is the note: {get_note_from_tab(d_natural_minor_harmonica, '-5')}")
print(f"Tab '1o' (overblow) is the note: {get_note_from_tab(d_natural_minor_harmonica, '1o')}")
print(f"Tab '10b' (blow bend) is the note: {get_note_from_tab(d_natural_minor_harmonica, '10b')}")