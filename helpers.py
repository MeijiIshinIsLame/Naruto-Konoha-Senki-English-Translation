from pathlib import Path
SJIS_FIRSTBYTE_LOWEST = 0x81
SJIS_FIRSTBYTE_HIGHEST = 0xFC
SJIS_SECONDTBYTE_LOWEST = 0x40
SJIS_SECONDTBYTE_HIGHEST = 0x7E
sjis_table_file = sjis_table_file = Path("config", "sjis.tbl")

def list_of_sjis_in_bytes(sjis_table_file):
    lines = None
    hex_values = []
    with open(sjis_table_file, "r", encoding="shift-jis") as f:
        lines = f.readlines()
    for line in lines:
        hex_str, char = line.split("=", 1)
        b = bytes.fromhex(hex_str)   # convert hex string → bytes
        hex_values.append(b)
    return hex_values

def is_1byte_sjis(byte):
    if len(byte) != 1:
        return False
    byte = int.from_bytes(byte)
    if byte >= 0x20 and byte <= 0x7e:
        result = True
    return False
    
def is_2byte_sjis(the_bytes):
    if len(the_bytes) <= 1:
        return False
    byte1_int = the_bytes[0]
    byte2_int = the_bytes[1]
    byte_1_match = True if byte1_int >= SJIS_FIRSTBYTE_LOWEST and byte1_int <= SJIS_FIRSTBYTE_HIGHEST else False
    byte_2_match = True if byte2_int >= SJIS_SECONDTBYTE_LOWEST and byte2_int <= SJIS_SECONDTBYTE_HIGHEST else False
    if byte_1_match and byte_2_match:
        return True
    return False
    
def is_sjis(the_bytes):
    if len(the_bytes) == 1:
        return is_1byte_sjis(the_bytes)
    if len(the_bytes) == 2:
        return is_2byte_sjis(the_bytes)
    return False

def is_possible_partial_sjis(b):
    do_nothing = 0
    move_backwards = 1
    move_forward = 2
    if b[0] >= SJIS_FIRSTBYTE_LOWEST and b[0] <= SJIS_FIRSTBYTE_HIGHEST:
        return move_forward
    if 
    
def is_opcode(the_bytes):
    result = False
    try:
        the_bytes.decode("shift_jis")
    except UnicodeDecodeError:
        result = True
    return result