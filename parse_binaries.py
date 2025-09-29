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
        return "<HEX>" + b.hex() + "</HEX>"

    def read_addr(self, length=4):
        addr = self.f.read(length)
        return "<ADDR>" + addr.hex() + "</ADDR>"

    def read_sjis(self, length):
        the_bytes = self.f.read(length)
        return self.bytes_to_sjis(the_bytes)
    
    def bytes_to_sjis(self, b):
        the_bytes = b.decode("shift_jis", errors="hexreplace")
        return "<SJIS>" + the_bytes + "</SJIS>"
        
    def sjis_next_action_jikkou(self, next_action):
        do_nothing = 0
        move_backwards = 1
        move_forwards = 2
        b2 = bytes()
        if next_action == do_nothing: 
            return None
        if next_action == move_backwards:
            self.f.seek(-2, 1)
            b2 = self.f.read(2)
        if next_action == move_forwards:
            self.f.seek(-1, 1)
            b2 = self.f.read(2)
            
        b2_first_byte = bytes([b2[0]])    
        if helpers.is_sjis(b2):
            return b2
        elif helpers.is_sjis(b2_first_byte):
            self.f.seek(-1, 1)
            b2 = self.f.read(1)
            return b2
        else:
            return None
    
    def read_sjis_until_opcode(self):
        the_bytes = bytes()
        while True:
            b = self.f.read(1)
            if helpers.is_possible_partial_sjis(b):
                next_action = helpers.sjis_decoder_next_action(b)
                b2 = self.sjis_next_action_jikkou(next_action)
                if not b2:
                    break
                else:
                    the_bytes += b2 
                #print(b2)
        sjis = self.bytes_to_sjis(the_bytes)
        return sjis
        
    def read_opcode_until_sjis(self):
        the_bytes = bytes()
        while True:
            b = self.f.read(1)
            if helpers.is_possible_partial_sjis(b):
                next_action = helpers.sjis_decoder_next_action(b)
                b2 = self.sjis_next_action_jikkou(next_action)
                if not b2:
                    self.f.seek(-1, 1)
                    the_bytes += self.f.read(1)
                else:
                    break
                if self.f.tell() >= self.file_size:
                    break
        sjis = self.bytes_to_sjis(the_bytes)
        return sjis
        
    # def read_opcode_until_sjis(self):
        # reading = True
        # length = 0
        # original_position = self.f.tell()
        # while reading:
            # the_bytes = self.f.read(2)
            # if not the_bytes:
                # break
            # if helpers.is_sjis(the_bytes):
                # self.f.seek(self.f.tell() - len(the_bytes))
                # break
            # length += 1
            # print("here")
            # #print("f tell", self.f.tell(), "file size", self.file_size)
        # self.f.seek(original_position-self.f.tell(), 1)
        # opcode_bytes = self.read_direct_hex(length)
        # return opcode_bytes
            
                
    def read_sjis_and_opcodes(self):
        string = ""
        #we can read opcodes at end because the file always ends in opcodes
        while self.f.tell() <= self.file_size:
            string += self.read_sjis_until_opcode()
            string += self.read_opcode_until_sjis()
            print(string)
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

    def search_bytes(self, pos, the_bytes):
        previous_pos = self.f.tell()
        self.f.seek(pos)
        data = self.f.read(len(the_bytes))
        result = data == the_bytes
        self.f.seek(previous_pos)
        return result

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
            part2 = self.read_sjis(remaining_file)
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
        for file in tqdm(files, desc="Processing files"):
            result = ""
            #print(file)
            with open(file, "rb") as file_handle:
                self.f = file_handle  # bind file handle to self
                self.file_size = os.path.getsize(file)  # bind filesize to self
                while self.f.tell() < self.file_size:
                    opcode = int.from_bytes(self.f.read(1))
                    opcode_result_bytes = self.process_opcode(opcode)
                    if opcode_result_bytes:
                        result += opcode_result_bytes
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