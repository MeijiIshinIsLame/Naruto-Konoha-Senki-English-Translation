import io
import os
import re
import helpers
from pathlib import Path
import codecs
from tqdm import tqdm
import shutil

INPUT_FOLDER = Path("english_script_files")

class Script:
    def __init__(self, path):
        self.path = Path(path)
        self.contents = self.parse_script()
        self.base_addr = int(self.path.stem, 16)
    
    def parse_script(self):
        tag_re = re.compile(r"<(HEX|ADDR|SJIS)>(.*?)</\1>", re.DOTALL)
        data = ""
        out = []
        with open(self.path, "r", encoding="shift_jis") as f:
            data = f.read()
        for tag, body in tag_re.findall(data):
            body = body.strip()
            if tag == "HEX":
                out.append((tag, bytes.fromhex(body)))
            elif tag == "ADDR":
                out.append((tag, bytes.fromhex(body)))
            elif tag == "SJIS":
                out.append((tag, body.encode("shift_jis")))
            else:
                out.append((tag, body))
        return out

class ROM:
    def __init__(self, path):
        self.startpos = 0x5AE750
        self.input_path = Path(path)
        self.output_path = self.input_path.with_stem(self.input_path.stem + "-output") #neruto-output.gba
        self.dialog_ptr_table = self.get_dialog_ptr_table()
    
    def get_dialog_ptr_table(self):
        start = 0x60C78
        end =  0x60FAB
        ptr_list = []
        with open(self.input_path, "rb") as f:
            f.seek(start)
            while f.tell() <= end:
                ptr = f.read(4)
                ptr_list.append(ptr)
        return ptr_list
    
    def update_ptr_table(self, old_addr, new_addr):
        for i, item in enumerate(self.dialog_ptr_table):
            #print("pos", i, "item in list", hex(int.from_bytes(item, byteorder="little")), "replacing", hex(int.from_bytes(old_addr, byteorder="little")), "with", hex(int.from_bytes(new_addr, byteorder="little")))
            if old_addr == item:
                self.dialog_ptr_table[i] = new_addr         
                
    def reinsert_ptr_table(self):
        start = 0x60C78
        with open(self.output_path, "r+b") as f:
            f.seek(start)
            for addr in self.dialog_ptr_table:
                f.write(addr)
    
    def insert_bytes_at_pos(self, pos, b):
        with open(self.output_path, "r+b") as f:
            f.seek(pos)
            f.write(b)
            self.startpos = f.tell()
    
    def insert_bytes(self, script):
        b = bytes()
        script_base_addr_bytes = script.base_addr.to_bytes(4, "little")
        new_base_addr_bytes = self.startpos + 0x8000000
        new_base_addr_bytes = new_base_addr_bytes.to_bytes(4, "little")
        self.update_ptr_table(script_base_addr_bytes, new_base_addr_bytes)
        for item in script.contents:
            if item[0] == "ADDR":
                addr_int = int.from_bytes(item[1], byteorder="little")
                offset = addr_int - script.base_addr
                updated_addr = self.startpos + offset + 0x8000000
                updated_addr = updated_addr.to_bytes(4, "little")
                b += updated_addr
            else:
                b += item[1]
        self.reinsert_ptr_table()
        self.insert_bytes_at_pos(self.startpos, b)
            
                    
        
if __name__ == "__main__":
    files = [f for f in INPUT_FOLDER.iterdir() if f.is_file()]
    for file in files:
        script = Script(file)
        #print(script.contents)\
        gamepath = Path("game/neruto.gba")
        rom = ROM(gamepath)
        rom.insert_bytes(script)
        #print(rom.dialog_ptr_table)
        
        