import io
from pathlib import Path

ROM_ADDR_START = 0x08000000
ROM_ADDR_END = 0x087ffff0
LAST_DATA_ADDRESS = 0x085ae980
SEEK_FROM_CURRENT_POS = 1
GAME_PATH = Path("game/neruto.gba")

def convert_to_big_endian(addr):
    return addr[::-1]

def process_opcode(opcode, f):
    if opcode == b'\x15':
        return f.read(8)
    if opcode == b'\x1b':
        return get_all_dialog_in_table()
        
        