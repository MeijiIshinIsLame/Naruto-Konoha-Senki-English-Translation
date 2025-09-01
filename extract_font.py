import io
from pathlib import Path
from PIL import Image, ImageDraw

start_address = 0x9CD54

def load_sjis_table(filename=Path("font/sjis-utf8.tbl")):
    sjis_values = []
    with open(filename, "r") as f:
        for line in f:
            pair = tuple(line.split("=", 1))
            sjis_values.append(pair)
    print(sjis_values)
    return sjis_values
    
def hex_to_8bit_binary_string(val):
    binary_str = bin(val)[2:]
    binary_str_8bit = format(val, "08b")
    return binary_str_8bit

def chunk_bits(bits, size):
    return [bits[i:i+size] for i in range(0, len(bits), size)]

def draw_image(filepath, byte_data):
    width = 8
    height = 8
    img = Image.new("RGB", (width, height), "white")
    pixels = img.load()
    byte_to_color_dict = {"11": (0, 0, 0), "01": (128, 128, 128), "00": (255, 255, 255), "10": (0, 0, 0)}
    i = 0
    for b in byte_data:
        eight_bits = hex_to_8bit_binary_string(b)
        chunked_bits = chunk_bits(eight_bits, 2)
        reversed_bits = list(reversed(chunked_bits))
        chunked_bits = reversed_bits
        for bit_pair in chunked_bits:
            color = byte_to_color_dict[bit_pair]
            x = i % width
            y = i // width
            print("xy:", x, y)
            print("byte:", hex(b))
            print("-----------------")
            pixels[x, y] = color  
            i += 1
    img_big = img.resize((width * 8, height * 8), Image.NEAREST)
    img_big.save(filepath)
    

def extract_chars_from_rom(filename=Path("game/neruto.gba")):
    i = 0
    sjis_table = load_sjis_table()
    sjis_offset_thing = 32 #i dont know why but they use this to calculate initial offset before byte shift
    with open(filename, "rb") as f:
        for character in sjis_table:
            i+=1
            print(character[0])
            hex_value = character[0]
            character_value = character[1]
            #print(hex(hex_value))
            hv = int(hex_value, 16)
            print("hv", hv)
            byte_amount_to_offset = (hv - sjis_offset_thing) << 4
            print(f"BTYE OFFSET 0x{byte_amount_to_offset:04X}")
            start_of_char_bytes = start_address + byte_amount_to_offset
            f.seek(start_of_char_bytes)
            char_bytes = f.read(16)
            print(f"0x{start_of_char_bytes:04X}")
            print(char_bytes.hex(' '))
            draw_image(Path(f"font/test{i}.png"), char_bytes)
            
            
            
extract_chars_from_rom()
        
        