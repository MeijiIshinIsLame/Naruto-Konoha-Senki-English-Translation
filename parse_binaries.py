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
        codecs.register_error("hexreplace", self.hex_fallback)

    def hex_fallback(self, error):
        bad_bytes = error.object[error.start:error.end]
        hex_repr = "<HEX>" + str(bad_bytes.hex()) + "</HEX>"
        return hex_repr, error.end

    def get_remaining_file(self):
        previous_pos = self.f.tell()
        remaining_file = self.f.read()
        self.f.seek(previous_pos)
        return remaining_file

    def read_direct_hex(self, length):
        the_bytes = self.f.read(length)
        return self.bytes_to_formatted_hex(the_bytes)
        
    def bytes_to_formatted_hex(self, b):
        return "<HEX>" + b.hex() + "</HEX>\n"

    def read_addr(self, length=4):
        addr = self.f.read(length)
        return "<ADDR>" + addr.hex() + "</ADDR>\n"

    def read_sjis(self, length):
        the_bytes = self.f.read(length)
        return self.bytes_to_sjis(the_bytes)
    
    def bytes_to_sjis(self, b):
        the_bytes = None
        print(hex(int.from_bytes(b)))
        try:
            the_bytes = b.decode("shift_jis")
        except:
            the_bytes = f"<ERROR>{b}</ERROR>"
        return "<SJIS>" + the_bytes + "</SJIS>\n"
    
    def read_sjis_until_opcode(self):
        stop_codes = [0x0, 0x1, 0x2, 0xff, 0x8]
        b = self.f.read(1)
        sjis = bytes()
        while int.from_bytes(b) not in stop_codes:
            sjis += b
            b = self.f.read(1)
        return self.bytes_to_sjis(sjis)
        
    def read_opcode_until_sjis(self):
        b = self.f.read(1)
        b2 = self.f.read(2)
        if not b2:
            return None
        opcodes = bytes()
        while not helpers.is_sjis(b2) or not b2:
            opcodes += b
            b = self.f.read(1)
            b2 = self.f.read(2)
            if self.f.tell() == self.file_size:
                break
        return self.bytes_to_formatted_hex(opcodes)
        
                
    def read_sjis_and_opcodes(self):
        string = ""
        #we can read opcodes at end because the file always ends in opcodes
        while self.f.tell() <= self.file_size:
            try:
                string += self.read_sjis_until_opcode()
                string += self.read_opcode_until_sjis()
                print(string)
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
        
        

    def read_script_data(self, length):
        pass

    def read_dialog(self, length):
        pass

    def process_opcode(self, opcode):
        if opcode == 0x01:
            self.f.seek(self.f.tell() - 1)
            tachiirikinshi_length = 26 #we jus kno brah
            part1 = self.read_direct_hex(1)
            part2 = self.read_sjis(tachiirikinshi_length)
            remaining_file = len(self.get_remaining_file())
            part3 = self.read_direct_hex(remaining_file)
            string = part1 + part2 + part3
            #print(string)
            return string

        if opcode == 0x15:
            self.f.seek(self.f.tell() - 1)
            part1 = self.read_direct_hex(4)
            part2 = self.read_addr(4)
            string = part1 + part2
            #print(string)
            return string

        if opcode == 0x22:
            self.f.seek(self.f.tell() - 1)
            part1 = self.read_direct_hex(16)
            remaining_file = len(self.get_remaining_file())
            part2 = self.read_sjis_and_opcodes()
            string = part1 + part2
            #print(string)
            return string

        if opcode == 0x1B:
            self.f.seek(self.f.tell() - 1)
            header = self.read_1b_header()
            string = header + self.read_sjis_and_opcodes()
            #print(string)
            return string
       
            

        # opcodes not handled yet
        return None

    def process_file(self, file_path=None):
        folder = Path(file_path) if file_path else self.INPUT_FOLDER
        files = [f for f in folder.iterdir() if f.is_file()]
        for file in files:
            result = ""
            #print(file)
            with open(file, "rb") as file_handle:
                self.f = file_handle  # bind file handle to self
                self.file_size = os.path.getsize(file)  # bind filesize to self
                while self.f.tell() <= self.file_size:
                    opcode = int.from_bytes(self.f.read(1))
                    opcode_result_bytes = self.process_opcode(opcode)
                    if opcode_result_bytes:
                        result += opcode_result_bytes
                    else: break
            out_file = OUTPUT_FOLDER / file.name
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