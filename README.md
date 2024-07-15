# CPS1-OKI-Generator
Python Script meant to convert .wav files to a CPS1 OKI (Samples) ROM

As simple as it's gonna get! A Python script designed to import 16-bit Signed PCM 7575 hz wav files in a folder named input_wav, and spits out an OKI ROM readable by the CPS1, pointers and compression and all! Only thing is the compression doesn't seem to be perfect as there's oftentimes clicking present, btu I think it's usable enough to share and get more eyes on

Inspired by the work of Fabian Sangliard, writer of the Book of CP System and the creator of CCPS (CPS1 SDK)
https://github.com/fabiensanglard/ccps/blob/master/oki/adpcm.go
