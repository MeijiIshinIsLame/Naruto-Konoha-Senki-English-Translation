import json
import io
from pathlib import Path

CONFIG_PATH = Path("config/extract_config.json")
MARKERS_PATH = Path("config/markers.json")
IGNORE_PATH = Path("config/ignore.txt")

################# helpers ##################

#byte string must start with 0x
def convert_string_to_byte_array(input_string):
    s = input_string.strip().removeprefix("0x")
    if len(s) % 2:  # handle odd digit counts gracefully
        s = "0" + s
    return int(s, 16).to_bytes(len(s) // 2, byteorder="big")

def get_character_name_from_bytes(bytes):
    # Find the matching name
    character_name = None
    for entry in markers:
        if entry['value'] == bytes:
            character_name = entry['name']
            break
    return character_name

############################################


def load_config():
    cfg = ""
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg

def load_markers():
    markers = ""

    with MARKERS_PATH.open("r", encoding="utf-8") as f:
        markers = json.load(f)

    for marker in markers:
        marker["value"] = convert_string_to_byte_array(input_string=marker["value"])

    return markers
    
def load_ignore_list():
    with open(IGNORE_PATH) as f:
        hex_strings = [line.strip() for line in f if line.strip()]

    byte_arrays = [convert_string_to_byte_array(input_string=h) for h in hex_strings]
    print(byte_arrays)
    return byte_arrays
    



config = load_config()
markers = load_markers()
ignore_list = load_ignore_list()

print(config)
print(markers)
print(ignore_list)



class Marker:
    def __init__(self, position, length):
        self.position = position
        self.length = length

    def __eq__(self, other):
        if not isinstance(other, Marker):
            return NotImplemented
        return (self.position, self.length) == (other.position, other.length)

    def __hash__(self):
        return hash((self.position, self.length))


class DialogScene:
    def __init__(self, start_address, end_address, input_filename, output_filename):
        self.start_address = int(start_address, 16)
        self.end_address = int(end_address, 16)
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.ignore_positions = set()
        self.marker_positions = set()
        self.byte_stream = self.get_byte_stream()
        self.full_bytes = self.get_full_filebytes()

    def get_full_filebytes(self):
        with open(self.input_filename, "rb") as f:
            file_bytes = io.BytesIO(f.read())
        return file_bytes
    
    def get_byte_stream(self):
        dialog_bytes_length = self.end_address - self.start_address
        with self.input_filename.open("rb") as f:
            f.seek(self.start_address)
            bytes = f.read(dialog_bytes_length)
        return io.BytesIO(bytes)
    
    def find_position_in_main_file(self, bytes):
        possible_match_positions = []
        
        first_byte = bytes[:1]
        self.full_bytes.seek(self.start_address)
        byte_data = True

        while self.full_bytes.tell() != self.end_address:
            byte_data = self.full_bytes.read(1)
            if byte_data == first_byte:
                possible_match_positions.append(self.full_bytes.tell())

        self.full_bytes.seek(self.start_address)
        
        if possible_match_positions:
            read_length = len(bytes)
            for i in possible_match_positions:
                self.full_bytes.seek(i - 1)
                bytes_to_check = self.full_bytes.read(read_length)
                if bytes_to_check == bytes:
                    position = self.full_bytes.tell()
                    return position
        else:
            return None
    
    def get_ignore_positions(self):
        #we look one byte at a time to get the list of possible positions first
        #then, we check again at all these positions to make sure if theyre actual matches or not
        possible_match_positions = []
        
        for hex_value in ignore_list:
            first_byte = hex_value[:1]
            self.byte_stream.seek(0)
            byte_data = 1
            
            while byte_data:
                byte_data = self.byte_stream.read(1)
                if byte_data == first_byte:
                    possible_match_positions.append(self.byte_stream.tell())
                    
            self.byte_stream.seek(0)
            
            if possible_match_positions:
                for hex_value in ignore_list:
                    read_length = len(hex_value)
                    for i in possible_match_positions:
                        self.byte_stream.seek(i - 1)
                        bytes_to_check = self.byte_stream.read(read_length)
                        if bytes_to_check == hex_value:
                            self.ignore_positions.add(Marker(position=i-1, length=read_length)) 
        sorted_ignore_positions = sorted(self.ignore_positions, key=lambda m: m.position)
        self.ignore_positions = sorted_ignore_positions


    def get_marker_positions(self):
        #we look one byte at a time to get the list of possible positions first
        #then, we check again at all these positions to make sure if theyre actual matches or not
        possible_match_positions = []
        
        for marker in markers:
            hex_value = marker["value"]
            first_byte = hex_value[:1]
            self.byte_stream.seek(0)
            byte_data = 1
            
            while byte_data:
                byte_data = self.byte_stream.read(1)
                if byte_data == first_byte:
                    possible_match_positions.append(self.byte_stream.tell())
                    
            self.byte_stream.seek(0)
            
            if possible_match_positions:
                for marker in markers:
                    hex_value = marker["value"]
                    read_length = len(hex_value)
                    for i in possible_match_positions:
                        self.byte_stream.seek(i - 1)
                        bytes_to_check = self.byte_stream.read(read_length)
                        if bytes_to_check == hex_value:
                            self.marker_positions.add(Marker(position=i-1, length=read_length))  
        sorted_marker_positions = sorted(self.marker_positions, key=lambda m: m.position)
        self.marker_positions = sorted_marker_positions

    def extract_text(self):
        #header = "start_position,end_position,character_name,sjis_hex,utf-8_text"
        for current_marker in self.marker_positions:

            self.byte_stream.seek(current_marker.position)

            character_bytes = self.byte_stream.read(current_marker.length)
            character_name = get_character_name_from_bytes(character_bytes)
            dialog_bytes = bytes()

            dialog = True

            while dialog:

                for ignore_item in self.ignore_positions:
                    if ignore_item.position == self.byte_stream.tell():
                        if not dialog_bytes:
                            self.byte_stream.read(ignore_item.length)
                        else:   
                            dialog = False
                
                for marker in self.marker_positions:
                    if marker != current_marker and marker.position == self.byte_stream.tell():
                        break
                

                dialog_bytes += self.byte_stream.read(1)
                if self.byte_stream.tell() >= len(self.byte_stream.getvalue()):
                    dialog = False
            dialog_without_last_byte = dialog_bytes[:-1]
            dialog_bytes = dialog_without_last_byte
            character_name_start_position = self.start_address + current_marker.position
            dialog_start_position = character_name_start_position + 4
            print("---------------------------------------------")
            print("character_name_start_position:", f"0x{character_name_start_position:08X}")
            print("character_bytes:", character_bytes.hex())
            print("character_name:", character_name)
            print("dialog_start_position:", f"0x{dialog_start_position:08X}")
            print("dialog_bytes:", dialog_bytes.hex())
            print("Dialog in Shift-JIS:", dialog_bytes.decode('shift_jis', errors='replace'))


for item in config:
    print("###########################################")     
    dialog = DialogScene(start_address=item["start_address"],
                        end_address=item["end_address"],
                        input_filename=Path("game/neruto.gba"),
                        output_filename=item["name"])

    dialog.get_ignore_positions()
    dialog.get_marker_positions()
    dialog.extract_text()
#print(dialog.ignore_positions)
#print(dialog.marker_positions)
#todo: make list of positions by looking for that exact hex. determine by size what blocks to look.