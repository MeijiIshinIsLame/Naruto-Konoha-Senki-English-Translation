import io
from pathlib import Path
GAME_PATH = Path("game/neruto.gba")
OUTPUT_FOLDER = Path("binary_files")
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

def convert_to_big_endian(addr):
    return addr[::-1]


def unique_filepath(base_name, ext = ".bin") -> Path:
    path = Path(OUTPUT_FOLDER / f"{base_name}{ext}")
    counter = 2
    while path.exists():
        path = Path(OUTPUT_FOLDER / f"{base_name}_{counter}{ext}")
        counter += 1
    return path    

def delete_all_files_in_output_folder():
    for item in OUTPUT_FOLDER.iterdir():
        if item.is_file():
            item.unlink()  # Deletes the file
 

def create_pointerlist(start_addr, end_addr):
    pointers_list = []
    with open(GAME_PATH, "rb") as f:
        f.seek(start_addr)
        while f.tell() <= end_addr:
            pointer = int.from_bytes(f.read(4), byteorder="little")
            if pointer != 0 and pointer not in pointers_list: 
                pointers_list.append(pointer)
    return pointers_list
            
            
def create_bins_from_pointerlist(pointerlist):
    delete_all_files_in_output_folder() #start with blank path
    for i in range(0, len(pointerlist)):
        binary_output = bytes()
        current_pointer = pointerlist[i]
        next_pointer = None
        
        #we do a little hardcoding round here
        #the if and elif are for stuff where i dont know how to deliminate end
        if pointerlist[i] == 0x805c6d3:
            final_dialog_length = 1650
            next_pointer = current_pointer + final_dialog_length
        else:
            next_pointer = pointerlist[i+1]
            
            
        with open(GAME_PATH, "rb") as f:
            f.seek(current_pointer-0x08000000)
            while f.tell() != next_pointer-0x08000000:
                byte = f.read(1)
                binary_output += byte
            bin_filepath = unique_filepath(base_name=f"{hex(current_pointer)}", ext=".bin")
            #print(f"processing {bin_filepath}")
            with open(bin_filepath, "wb") as f2:
                f2.write(binary_output)
    print("done")
                
            
#pointers = create_pointerlist(start_addr=0x60c78, end_addr=0x60e30)
#pointers= create_pointerlist(start_addr=0x60ef4, end_addr=0x60fa8)

pointerlist= create_pointerlist(start_addr=0x60c78, end_addr=0x60fa8)
pointerlist.sort()

for i in pointerlist:
    print(hex(i))
    
create_bins_from_pointerlist(pointerlist)