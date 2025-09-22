<h2><span style="color:red">15</span> 00 0E 01 57 B9 04 08 <span style="color:red">15</span> 03 E5 00 57 B9 04 08 <span style="color:red">15</span> 03 50 00 B5 B5 04 08 <span style="color:red">15</span> 03 45 00 A7 AF 04 08 <span style="color:red">15</span> 03 1B 00 6A A9 04 08 <span style="color:red">1B</span> <span style="color:orange">04</span> 00 23 00 02 23 00 03 02 00 <span style="color:blue">01 01</span> <span style="color:brown">20 01</span></h2>


15 <span style="color:red">00 0E 01</span> **57 B9 04 08**
15 <span style="color:red">03 E5 00</span> **57 B9 04 08**
15 <span style="color:red">03 50 00</span> **B5 B5 04 08**
15 <span style="color:red">03 45 00</span> **A7 AF 04 08**
15 <span style="color:red">03 1B 00</span> **6A A9 04 08**
1B 04 00 23 00 02 23 00 03 02 00 01 01 **20** 01

the order is likely backwards. Could it be little endian 3 byte scene id?

endings
**00 19 00 36 36 19 01 32 32 00**
1b = 0804a96a

00 14 1E **00 19 00 36 36 19 00 32 32** 19 01 27 27 00
1b = 0804afa7

00 1D 02 35 14 4F **00 19 00 36 36 19 01 32 32** 19 01 27 27 00
1b = 0804b5b5

**00 19 00 36 36 00**
1b = 0804b957

**00 19 00 36 36 00**
1b = 0804be31 - unused? There is no reference to this at all.

**00 19 00 36 36 00** this is probably just signaling the end. find out what these numbers mean and i think you win



write a program where you can manipulate this
just do it in python. write 4 bytes of the address you want to change to new naruto file and then run that.

Kakahshi Entrance Total Hex
00 03 FF 20 01 - idk yet maybe avatar
82 CD 82 BD 82 AF 83 4A 83 4A 83 56 - hatake kakashi name
00 01 81 - idk, avatar?
75 82 E2 81 5B 81 40 82 A8 82 DC 82 BD 82 B9 81 5B 81 76 - line
00 02 01 07 00 20 01 - idk yet maybe name thing
82 CD 82 BD 82 AF 83 4A 83 4A 83 56 - hatake kakashi name
00 11 01 01  - end nameplate? maybe kakashis nameplate?

Kakashi entr

try to use beginning codes from other areas
swap out ppls avatar and get list




beginning opcodes
03 01 01 -- before most battle scene tables