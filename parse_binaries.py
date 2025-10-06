import io
import os
import helpers
from pathlib import Path
import codecs
from tqdm import tqdm

INPUT_FOLDER = Path("binary_files")
OUTPUT_FOLDER = Path("script_files")

class BinaryScriptProcessor:
    def __init__(self, input_folder=INPUT_FOLDER, output_folder=OUTPUT_FOLDER):
        self.INPUT_FOLDER = Path(input_folder)
        self.OUTPUT_FOLDER = Path(output_folder)
        self.f = None  # will hold the current file handle
        self.file_size = 0

    def get_remaining_file(self):
        previous_pos = self.f.tell()
        remaining_file = self.f.read()
        self.f.seek(previous_pos)
        return remaining_file

    def read_direct_hex(self, length):
        the_bytes = self.f.read(length)
        return self.bytes_to_formatted_hex(the_bytes)
        
    def bytes_to_formatted_hex(self, b):
        return "<HEX>" + b.hex() + "</HEX>"

    def read_addr(self, length=4):
        
        addr = self.f.read(length)
        #if not addr: return None
        return "\n<ADDR>" + addr.hex() + "</ADDR>\n"
    
    def read_until_address(self):
        bytestring = bytes()
        b_addr = self.f.read(4)
        self.f.seek(-4, 1)
        print("b uninitiated", "b_addr", b_addr.hex())
        while not helpers.is_little_endian_address(b_addr):
            b = self.f.read(1)
            bytestring += b
            b_addr = self.f.read(4)
            print("b", b.hex(), "b_addr", b_addr.hex())
            if not b_addr:
                break
            if len(b_addr) < 4:
                bytestring += b_addr
                break
            self.f.seek(-4, 1)
        return "\n<HEX>" + bytestring.hex() + "</HEX>\n"
    
    def read_sjis(self, length):
        the_bytes = self.f.read(length)
        return self.bytes_to_sjis(the_bytes)
    
    def bytes_to_sjis(self, b):
        the_bytes = None
        try:
            the_bytes = b.decode("shift_jis")
            if the_bytes:
                return "\n<SJIS>" + the_bytes + "</SJIS>\n"
        except:
            return "\n<ERROR_DECODING_SJIS>" + the_bytes + "</ERROR_DECODING_SJIS>\n"
        return None
    
    def read_sjis_until_opcode(self):
        stop_codes = [0x0, 0x1, 0x2, 0xff]
        b = self.f.read(1)
        if b in stop_codes:
            self.f.seek(-1, 1)
            return None
        sjis = bytes()
        while int.from_bytes(b) not in stop_codes:
            sjis += b
            b = self.f.read(1)
        self.f.seek(-1, 1)
        return self.bytes_to_sjis(sjis)
        
    def read_opcode_until_sjis(self):
        b = self.f.read(1)
        b2 = self.f.read(2)
        if not b2:
            return None
        self.f.seek(-2, 1)
        opcodes = bytes()
        while not helpers.is_sjis(b2):
            opcodes += b
            b = self.f.read(1)
            b2 = self.f.read(2)
            if self.f.tell() >= self.file_size:
                break
            self.f.seek(-2, 1)
        opcodes += b
        if self.f.tell() >= self.file_size:
            opcodes += b2
        return self.bytes_to_formatted_hex(opcodes)
        
                
    def read_sjis_and_opcodes(self):
        string = ""
        #we can read opcodes at end because the file always ends in opcodes
        while self.f.tell() <= self.file_size:
            try:
                string += self.read_sjis_until_opcode()
                string += self.read_opcode_until_sjis()
            except:
                break
        return string
                
        
    def read_1b_header(self):
        header_bytes = bytes()
        original_position = self.f.tell()
        while not helpers.is_sjis(self.f.read(2)):
            self.f.seek(self.f.tell() - 2)
            header_bytes += self.f.read(1)
        return self.bytes_to_formatted_hex(header_bytes)
        
       
    def process_opcode(self, opcode):
        if opcode == 0x01:
            self.f.seek(self.f.tell() - 1)
            part1 = self.read_direct_hex(1)
            part2 = self.read_sjis_and_opcodes()
            string = part1 + part2
            #print(string)
            return self.read_direct_hex(self.file_size) #fix this later
            
        if opcode == 0x12:
            self.f.seek(self.f.tell() - 1)
            header = self.read_opcode_until_sjis()
            return header + self.read_sjis_and_opcodes()
            
        if opcode == 0x15:
            self.f.seek(self.f.tell() - 1)
            part1 = self.read_direct_hex(4)
            part2 = self.read_addr(4)
            return part1 + part2
        
        if opcode == 0x16:
            self.f.seek(self.f.tell() - 1)
            return self.read_direct_hex(self.file_size)

        if opcode == 0x22:
            self.f.seek(self.f.tell() - 1)
            part1 = self.read_direct_hex(16)
            part2 = self.read_sjis_and_opcodes()
            return part1 + part2
        
        if opcode == 0x32:
            self.f.seek(self.f.tell() - 1)
            part1 = self.read_direct_hex(1)
            part2 = self.read_addr(4)
            return part1 + part2
        
        
        if opcode == 0x33:
            self.f.seek(self.f.tell() - 1)
            part1 = self.read_until_address()
            part2 = self.read_addr(4)
            return part1 + part2
        
        if opcode == 0x34:
            self.f.seek(self.f.tell() - 1)
            part1 = self.read_direct_hex(4)
            part2 = self.read_addr(4)
            return part1 + part2
        
        if opcode == 0x1B:
            self.f.seek(self.f.tell() - 1)
            header = self.read_opcode_until_sjis()
            return header + self.read_sjis_and_opcodes()
        
        if opcode == 0x0B:
            self.f.seek(self.f.tell() - 1)
            part1 = self.read_direct_hex(2)
            part2 = self.read_addr(4)
            return part1 + part2
        
        if opcode == 0x08:
            self.f.seek(self.f.tell() - 1)
            part1 = self.read_opcode_until_sjis()
            part2 = self.read_sjis_and_opcodes()
            return part1 + part2
            
        if opcode == 0x1E:
            self.f.seek(self.f.tell() - 1)
            return self.read_direct_hex(self.file_size)

        if opcode == 0x0C:
            self.f.seek(self.f.tell() - 1)
            part1 = self.read_direct_hex(2)
            part2 = self.read_addr(4)
            part3 = self.read_sjis_and_opcodes()
            return part1 + part2 + part3
            
        if opcode == 0x07:
            self.f.seek(self.f.tell() - 1)
            part1 = self.read_direct_hex(1)
            part2 = self.read_addr(4)
            part3 = self.read_direct_hex(1)
            return part1 + part2 + part3
        
        # opcodes not handled yet
        return self.read_sjis_and_opcodes()

    def process_file(self, file_path=None):
        folder = Path(file_path) if file_path else self.INPUT_FOLDER
        files = [f for f in folder.iterdir() if f.is_file()]
        for file in tqdm(files):
            result = ""
            #print(file)
            with open(file, "rb") as file_handle:
                self.f = file_handle  # bind file handle to self
                self.file_size = os.path.getsize(file)  # bind filesize to self
                while self.f.tell() <= self.file_size:
                    print(file.name)
                    opcode = int.from_bytes(self.f.read(1))
                    print(hex(opcode))
                    opcode_result_bytes = self.process_opcode(opcode)
                    if opcode_result_bytes:
                        result += opcode_result_bytes
                    else: break
            out_file = OUTPUT_FOLDER / Path(file.name).with_suffix(".txt")
            with open(out_file, "w", encoding="shift_jis") as output_file_handle:
                output_file_handle.write(result)
                


if __name__ == "__main__":
    processor = BinaryScriptProcessor()
    processor.process_file()
        
# def process_file(file_path):
    # files = [f for f in file_path.iterdir() if f.is_file()]
    # for file in files:
        # print(file)
        # with open(file, "rb") as f:
            # file_size = os.path.getsize(file)
            # while f.tell() < file_size:
                # opcode = int.from_bytes(f.read(1))
                # process_opcode(opcode, f)