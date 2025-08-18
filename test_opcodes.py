import argparse
from pathlib import Path
import json

CONFIG_PATH = Path("config/replacement_locations_for_test.json")
SOURCE_FILE = Path("game/neruto.gba")

def overwrite_location_bytes(location, bytes_to_overwrite, source_file, dest_file):
    source_file_data = source_file.open("rb").read()
    the_bytes = bytes()
    with source_file.open("rb") as f:
        f.seek(0)
        while f.tell() != len(source_file_data):
            the_bytes += f.read(1)
            if f.tell() == location:
                print("found")
                the_bytes += bytes_to_overwrite
                f.seek(location + len(bytes_to_overwrite))
                the_bytes += f.read(abs(f.tell() - len(source_file_data)))
              
    
    with dest_file.open("w+b") as f:
        f.write(the_bytes)
    
    print("written to", dest_file)




def parse_config(config_path):
    cfg = ""
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg

############# main #############

config = parse_config(CONFIG_PATH)
for item in config:
    location = int(item['location'], 16)
    bytes_to_overwrite = bytes.fromhex(item['bytes'])
    source_file = SOURCE_FILE
    dest_file = Path(f"testfiles/Replace_bytes_{item['bytes']}_at_loc_{item['location']}.gba")

    overwrite_location_bytes(location, bytes_to_overwrite, source_file, dest_file)