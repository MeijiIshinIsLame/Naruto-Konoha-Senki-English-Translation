text routine finds which dialog to snatch with the instructions at 0808f544
the value of r4 is shifted left 10h, right Eh, and then added to 08060d54 and read into memory

at 080977d8, the initialization point of the text area is loaded.
1 byte is loaded into r0
that byte is shifted left 2h  (15 becomes 54)
THIS IN HEX is turned into an int (54h is 54) and thats the header length of the dialog before it starts.

script id is saved at 020311ea


08060d54 - some of the text location references
**How to read these?**
Theyre little endian 16 bit addresses, and the 08 is from ROM.
![[Pasted image 20250913163852.png]]


now that you have the text routine, you can work on replacing the text and then replacing the locs as well. Do a dump first.

![[Pasted image 20250913234843.png]]

01 right before name = start