import io
from pathlib import Path
from tqdm import tqdm

START_POS = 4 #we read 4 bytes at a time, so its gotta start from 4 because it is little endian
ROM_ADDR_START = 0x08000000
ROM_ADDR_END = 0x087ffff0
LAST_DATA_ADDRESS = 0x085ae980
SEEK_FROM_CURRENT_POS = 1
GAME_PATH = Path("game/neruto.gba")
CSV_OUTPUT_PATH = Path("config/pointers.csv")

def convert_to_big_endian(addr):
    return addr[::-1]

def area_has_pointer_address(f, current_byte):
    original_pos = f.tell()
    if current_byte == b'\x08':
        f.seek(-4, SEEK_FROM_CURRENT_POS)
        addr_little_endian = f.read(4)
        f.seek(original_pos)
        addr_big_endian = convert_to_big_endian(addr_little_endian)
        #maybe make sure the nextdoor byte isnt 08 as well? not sure
        addr_value = int.from_bytes(addr_big_endian, "big")
        if addr_value <= LAST_DATA_ADDRESS and addr_value >= ROM_ADDR_START:
            f.seek(addr_value - ROM_ADDR_START)
            the_byte = f.read(1)
            f.seek(original_pos)
            if the_byte != b'\x00':
                return addr_big_endian.hex()
    #else catch all
    f.seek(original_pos)
    return False
    

def get_address_dict_from_rom(filepath):
    dict_of_pointers = {}
    with open(filepath, "rb") as f:
        f.seek(START_POS)
        for i in tqdm(range(LAST_DATA_ADDRESS - ROM_ADDR_START)):
            current_byte = f.read(1)
            if not current_byte:
                break
            pointer = area_has_pointer_address(f, current_byte)
            if pointer:
                current_addr = f"0x{f.tell():08X}"
                dict_of_pointers[current_addr] = pointer
    return dict_of_pointers
        
    
def build_csv(addr_dict, output_file):
    print("writing csv")
    with open(output_file, "w") as f:
        header = "address,pointer\n"
        f.write(header)
    with open(output_file, "a") as f:
        for address, pointer in addr_dict.items():
            f.write(f"{address},{pointer}\n")
    print("done")
        
    
    
pointer_dict = get_address_dict_from_rom(GAME_PATH)
#print(pointer_dict)
build_csv(pointer_dict, CSV_OUTPUT_PATH)
    