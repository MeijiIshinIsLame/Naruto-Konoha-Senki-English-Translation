#####################################################
#  USE THIS FILE TO REPLACE FIRST SCENE FOR TESTING #
#####################################################

import io
from pathlib import Path
import argparse

game_path = Path("game/neruto.gba")
output_path = Path("game/scene_edited_neruto.gba")
#start_address = 0x60d4c

def replace_address(start_address, address_replacement):
    start_address = int(start_address, 16)
    print(start_address)
    address_replacement = int(address_replacement, 16)
    address_replacement = address_replacement.to_bytes(4, byteorder="little")
    with open(game_path, "rb") as f:
        bytes_from_original = f.read()
        print("bytes read")
    full_bytes = io.BytesIO(bytes_from_original)
    beginning_half = full_bytes.read(start_address)
    full_bytes.read(4) #skip the bytes we wanna replace
    end_half = full_bytes.read()
    print("writing replacement")
    with open(output_path, "wb") as f:
        f.write(beginning_half)
        f.write(address_replacement)
        f.write(end_half)
    print("finished")
             
if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser()
    
    # Add one argument
    parser.add_argument("source_addr", help="address, ex 0x08034647")
    parser.add_argument("new_addr", help="address, ex 0x08034647")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Pass the argument to the function
    replace_address(args.source_addr, args.new_addr)