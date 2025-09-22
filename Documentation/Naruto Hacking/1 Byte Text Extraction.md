Start address of all 1byte text character pixels: 0x9CD54

character start position is calculated by:
((sjis_character_encoding_byte - 0x20) << 4) + start_address

Then, read 16 bytes (4 pixels per byte = 64 pixels total)

render them right to left. Each 2 bits of the byte corresponds to a color

11, 10 = black
01 = grey
00 = white

End result should be rendering of 4 blocks at a time, left to right, top to bottom, with the colors corresponding to each 2 bits.