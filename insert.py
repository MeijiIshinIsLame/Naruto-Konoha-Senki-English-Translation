import io
import json
import os
from pathlib import Path

ROMFILE = Path("game/neruto.gba")
OUTPUT = Path("game/neruto_translated.gba")
file_to_insert = Path("ichiraku_01.json")

def string_to_shiftjis(text):
    pass

def load_translated_file(filename):
    cfg = ""
    with filename.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg
    
new_bytes = bytes()

translated_dialog = load_translated_file(file_to_insert)
start_position = int(translated_dialog[0]["dialog_start_position"], 16)

full_romsize = 0

with open(ROMFILE, "rb") as f:
    full_romsize = f.read()
    full_romsize = len(full_romsize)
    
print(full_romsize)

with ROMFILE.open("rb") as f:
    new_bytes = f.read(start_position)
    
    for entry in translated_dialog:
        new_bytes += f.read(int(entry["dialog_start_position"], 16) - f.tell())
        english_dialog = entry["english"].encode("shift_jis")
        new_bytes += english_dialog
        skip_bytes_len = len(bytes.fromhex(entry["dialog_bytes"]))
        f.read(skip_bytes_len)
        
    new_bytes += f.read(full_romsize - f.tell())

target_size = full_romsize
source_size = len(new_bytes)

padding_needed = target_size - source_size
ff_padding = b"\xFF" * padding_needed
parts = [new_bytes, ff_padding]
new_bytes = b"".join(parts)
    
with open(OUTPUT, "wb") as f:
    f.write(new_bytes)
    
    
    

        
    
        
        