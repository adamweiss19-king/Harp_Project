import re

from data import all_harmonicas

# Harmonica Logic
#get all harmonica names
def get_all_harmonica_names():
    """Returns a list of all harmonica names."""
    return list(all_harmonicas.keys())

# select a harmonica dictionary by name
def get_harmonica_dict_by_name(harmonica_name):
    """Returns the harmonica dictionary for the given name, or None if not found."""
    return all_harmonicas.get(harmonica_name, None)



# 1. Create a set of all notes found in all harmonica dictionaries (from C1 up to the highest found)
#this may not actually be useful for anything but was part of discovery. maybe delete if don't use
def extract_all_notes(harmonica_dicts):
    notes = set()
    for hdict in harmonica_dicts:
        notes.update(hdict.values())
    return notes

#2 MIDI Functions
    #2a.Convert MIDI number back to note name
def note_to_midi(note):
    """Convert note name (e.g. 'C4', 'G#5') to MIDI number."""
    note_names = {
        'C':0, 'C#':1, 'Db':1, 'D':2, 'D#':3, 'Eb':3, 'E':4, 'F':5, 'F#':6, 'Gb':6,
        'G':7, 'G#':8, 'Ab':8, 'A':9, 'A#':10, 'Bb':10, 'B':11}
    m = re.match(r"([A-G][b#]?)(\d+)", note)
    if not m:
        return None
    name, octave = m.groups()
    return 12 + note_names[name] + 12 * int(octave)

    #2b. Convert MIDI number back to note name
def midi_to_note(midi):
    """Convert MIDI number to note name (e.g. 60 -> 'C4')."""
    note_names = {
        'C':0, 'C#':1, 'Db':1, 'D':2, 'D#':3, 'Eb':3, 'E':4, 'F':5, 'F#':6, 'Gb':6,
        'G':7, 'G#':8, 'Ab':8, 'A':9, 'A#':10, 'Bb':10, 'B':11}  
    octave = midi // 12 - 1
    note_name = list(note_names.keys())[midi % 12] 
    return f"{note_name}{octave}"

#3. Create all available notes (chromatically)
def get_all_chromatic_notes(min_midi, max_midi):
    return [midi_to_note(m) for m in range(min_midi, max_midi + 1)]

#4 Lookup note from tab in a given harmonica dictionary
def get_note_from_tab(harmonica_dict, tab):
    """
    Looks up a harmonica tab in a given dictionary and returns the note.
    """
    tab_str = str(tab)
    return harmonica_dict.get(tab_str, "Tab not found")

#4a. Find harmonicas that contain a given note
def find_harmonicas_with_note(note, all_harmonicas):
    """
    Returns a list of harmonica dictionary names and tabs that contain the given note.
    all_harmonicas should be a dict of {name: harmonica_dict}
    """
    results = []
    for name, hdict in all_harmonicas.items():
        for tab, n in hdict.items():
            if n == note:
                results.append((name, tab))
    return results

#5. Create a dictionary of easy-to-play notes (no overblows, no octaves)
def create_easy_to_play_harmonica(harmonica_dict):
    """
    Given a full harmonica dictionary, returns a dictionary of easy-to-play notes organized by octave.
    """
    easy_to_play = {}
    for tab, note in harmonica_dict.items():
        # Determine octave from note
        m = re.match(r"([A-G][b#]?)(\d+)", note)
        if m:
            if 'o' not in tab:
                easy_to_play[tab] = note
       
    return easy_to_play


#5a. Check how many notes from a given list are available in a given harmonica dictionary
def percent_notes_in_harmonica(notes, harmonica_dict):
    """
    Given a list of notes and a harmonica dictionary,
    returns the percentage of those notes that exist in the harmonica.
    """
    harmonica_notes = set(harmonica_dict.values())
    found = sum(1 for note in notes if note in harmonica_notes)
    percent = (found / len(notes)) * 100 if notes else 0
    return percent

# 5b. Check how many notes from a given list are available in all harmonica dictionaries
def percent_notes_in_all_harmonicas(notes, all_harmonicas):
    """
    For each harmonica, returns a tuple of (harmonica name, percent available, missing notes).
    """
    results = []
    notes_set = set(notes)
    for name, hdict in all_harmonicas.items():
        harmonica_notes = set(hdict.values())
        found = notes_set & harmonica_notes
        missing = list(notes_set - harmonica_notes)
        percent = (len(found) / len(notes)) * 100 if notes else 0
        results.append({
            "harmonica": name,
            "percent_available": percent,
            "missing_notes": missing
        })
    return 


## Song Logic

#1a. Input the information (picture of tabs, sheet music, individual notes or midi)
def input_song_notes(song_name,song_notes):
    """
    Placeholder function for inputting song notes.
    This could be extended to handle different input methods (e.g., image processing, MIDI files).
    """
    pass 

#1b. Store the information in a dictionary
def create_a_song(song_name, song_notes):
    """
    Store a song as a dictionary with its name and notes.
    """
    return {"name": song_name, "notes": song_notes}

#2. Convert the notes into MIDI numbers
def song_notes_to_midi(song):
    """
    Convert the notes in a song dictionary to MIDI numbers.
    Returns a new dictionary with MIDI numbers.
    """
    midi_numbers = [note_to_midi(note) for note in song["notes"]]
    return {"name": song["name"], "midi": midi_numbers}

#2a. Convert MIDI numbers into tabs for a given harmonica dictionary
def midi_to_tabs(midi_list, harmonica_dict):
    """
    Given a list of MIDI numbers and a harmonica dictionary,
    return a list of tabs (as strings) that play those MIDI notes.
    If a note is not found, 'N/A' is used.
    """
    # Build a lookup: midi_number -> tab(s)
    midi_to_tab = {}
    for tab, note in harmonica_dict.items():
        midi_num = note_to_midi(note)
        if midi_num is not None:
            midi_to_tab.setdefault(midi_num, []).append(tab)

    # For each midi in midi_list, get the first matching tab or 'N/A'
    tabs = []
    for midi in midi_list:
        if midi in midi_to_tab:
            tabs.append(midi_to_tab[midi][0])  # Use the first tab found
        else:
            tabs.append('N/A')
    return tabs
#3 Convert the song information into tabs
#3a Move the song up or down an octave when checking for which harmonica key makes the most sense
def shift_notes_by_octave(notes, shift):
    """
    Shift a list of note names up or down by 'shift' octaves.
    """
    shifted = []
    for note in notes:
        m = re.match(r"([A-G][b#]?)(\d+)", note)
        if m:
            name, octave = m.groups()
            new_octave = int(octave) + shift
            if new_octave >= 0:  # Avoid negative octaves
                shifted.append(f"{name}{new_octave}")
    return shifted

#3b. For each harmonica in all_harmonicas, convert the song MIDI to tabs and print the results, ordered by percent of notes available (descending)
def convert_midi_to_tabs_for_a_set_of_harmonicas(song, set_of_harmonicas):
    """
    For each harmonica in all_harmonicas, convert the song MIDI to tabs and print the results,
    ordered by percent of notes available (descending).
    Checks original, +1, +2, -1, -2 octaves and keeps the highest percent for each harmonica.
    """
    results = []
    octave_shifts = [0, 1, 2, 3, -1, -2, -3]
    for harmonica_name, harmonica_dict in set_of_harmonicas.items():
        best_percent = -1
        original_notes = song['notes']        
        best_tabs = []
        best_notes = []
        best_shift = 0
        for shift in octave_shifts:
            shifted_notes = shift_notes_by_octave(song['notes'], shift)
            midi = [note_to_midi(note) for note in shifted_notes if note_to_midi(note) is not None]
            tabs = midi_to_tabs(midi, harmonica_dict)
            percent = percent_notes_in_harmonica(shifted_notes, harmonica_dict)
            if percent > best_percent:
                best_percent = percent
                best_tabs = tabs
                best_notes = shifted_notes
                best_shift = shift
        results.append({
            "harmonica": harmonica_name,
            "tabs": best_tabs,
            "percent": best_percent,
            "notes": best_notes,
            "octave_shift": best_shift
        })
# Sort by percent descending
    results.sort(key=lambda x: x["percent"], reverse=True)

    # Pretty print
    for entry in results:
        print("="*40)
        print(f"Harmonica: {entry['harmonica']}")
        print(f"Best octave shift: {entry['octave_shift']}")
        print(f"Percent of notes available: {entry['percent']:.1f}%")
        print(f'Original Notes: {original_notes}')
        print("Notes: ", entry['notes'])
        print("Tabs:  ", entry['tabs'])
    print("="*40)
    return results

#3c. Same as above but using easy-to-play harmonica dictionaries
def convert_midi_to_easy_to_play_tabs_for_a_set_of_harmonicas(song, set_of_harmonicas):
    """
    For each harmonica in all_harmonicas, convert the song MIDI to tabs and print the results,
    ordered by percent of notes available (descending).
    Checks original, +1, +2, -1, -2 octaves and keeps the highest percent for each harmonica.
    """
    results = []
    octave_shifts = [0, 1, 2, -1, -2]
    for harmonica_name, harmonica_dict in set_of_harmonicas.items():
        best_percent = -1
        original_notes = song['notes']
        best_tabs = []
        best_notes = []
        best_shift = 0
        easy_harmonica_dict = create_easy_to_play_harmonica(harmonica_dict)
        for shift in octave_shifts:
            shifted_notes = shift_notes_by_octave(song['notes'], shift)
            midi = [note_to_midi(note) for note in shifted_notes if note_to_midi(note) is not None]
            tabs = midi_to_tabs(midi, easy_harmonica_dict)
            percent = percent_notes_in_harmonica(shifted_notes, easy_harmonica_dict)
            if percent > best_percent:
                best_percent = percent
                best_tabs = tabs
                best_notes = shifted_notes
                best_shift = shift
        results.append({
            "harmonica": harmonica_name,
            "tabs": best_tabs,
            "percent": best_percent,
            "notes": best_notes,
            "octave_shift": best_shift
        })

    # Sort by percent descending
    results.sort(key=lambda x: x["percent"], reverse=True)

    # Pretty print
    for entry in results:
        print("="*40)
        print(f"Harmonica: {entry['harmonica']} (Easy to Play)")
        print(f"Best octave shift: {entry['octave_shift']}")
        print(f"Percent of notes available: {entry['percent']:.1f}% (Easy to Play)")
        print(f'Original Notes: {original_notes}')
        print("Easy Notes: ", entry['notes'])
        print("Easy Tabs:  ", entry['tabs'])
    print("="*40)
    return results

