import os
import os, glob
import time
import sys

audio_inp_format = ".wav" #Format of choice, defaults to wav
wav_header_length = 0x28
#	Subchunk1ID   string // Must be "fmt " 0x10
#	Subchunk1Size uint32 // 16 for PCM 0x04
#	AudioFormat   uint16 // PCM = 1 0x02
#	NumChannels   uint16 // Mono 1, Stereo = 2, 0x02
#	SampleRate    uint32 // 44100 for CD-Quality 0x04
#	ByteRate      uint32 // SampleRate * NumChannels * BitsPerSample / 8 0x04
#	BlockAlign    uint16 // NumChannels * BitsPerSample / 8 (number of bytes per sample) 0x02
#	BitsPerSample uint16 // 8 bits, 16 bits.. 0x02
input_path  = "input_wav"
output_path = "compressed_wav"

if not os.path.exists(input_path):
    msg = str("No WAVs to compress! Ensure there's a folder named -{}- containing - ".format(input_path))
    msg += "\n16-Bit Signed PCM.WAV files, 7575hz\n"
    msg += "I'll go make it right quick, now go put stuff in it!\n"
    msg += "Press Enter to exit..."
    os.makedirs(input_path)
    input(msg)
    quit()

if not os.path.exists(output_path):
    print("Creating Output path...")
    os.makedirs(output_path)


def evaluate_input_wavs():
    names = {}
    index = 0
    for filename in glob.glob(os.path.join(input_path, '*.wav')):
        path = os.path.join(os.getcwd(), filename)
        outpath = filename.replace(input_path,output_path,1)
        with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
            print(filename," - ", outpath)
            names.update({index : filename})
            index += 1
    return names

def return_outnames():
    out_names = {}
    index = 0
    for i in range(0,len(pcmnames),1):
        outpath = pcmnames[i].replace(input_path,output_path,1)
        out_names.update({index : outpath})
        index += 1
    return out_names

#-------------------- FUNCTIONS --------------------
def return_pcm_name(name):
    pcmname = name + audio_inp_format
    pcmname = pcmname.lower()
    return pcmname

def close_program(msg,name,val):
    print(name, " - isn't formatted properly")
    string = str("{} - {}").format(msg,hex(val))
    sys.exit(string)

def to_array16(table):
    cursor = 0
    wav = bytearray(len(table))

    for i in range(0, len(table),2):
        wav[cursor] = table[cursor+1]
        wav[cursor+1] = table[cursor]
        cursor += 2
    return wav


#In order to properly compress, we need to ensure the format of the WAV file matches certain parameters
def format_PCM(table,name):
    debug = 1
    # Parse Header
    ChunkID = int.from_bytes(table[0:4], byteorder='big')
    if ChunkID != 0x52494646: #Hex representation of "RIFF"
        close_program("ERROR 1: No RIFF Identifier",name,ChunkID)
    if debug == 1:
        print("VALID 'RIFF' - \t\t\t", hex(ChunkID))

    ChunkSize = int.from_bytes(table[4:8], byteorder='little')
    if ChunkSize != len(table) - 8:
        close_program("ERROR 2: Invalid ChunkSize",name,ChunkSize)
    if debug == 1:
        print("VALID CHUNKSIZE - \t\t", hex(ChunkSize))

    Format = int.from_bytes(table[8:12], byteorder='big')
    if Format != 0X57415645: #Hex representation of "WAVE"
        close_program("ERROR 3: Bad WAVE Format",name,Format)
    if debug == 1:
        print("VALID WAVE FORMAT - \t\t", hex(Format))

    #Now parse "fmt" chunk
    data = table[12:len(table)]

    Subchunk1ID = int.from_bytes(data[0:4], byteorder='big')
    if Subchunk1ID != 0x666D7420: #Hex representation of "fmt "
        close_program("ERROR 4: Invalid Subchunk FMT",name,Subchunk1ID)
    if debug == 1:
        print("VALID SUBCHUNK ID FORMAT - \t", hex(Subchunk1ID))

    Subchunk1Size = int.from_bytes(data[4:8], byteorder='little')
    if Subchunk1Size != 0x00000010:
        close_program("ERROR 5: Invalid Subchunk Size",name, Subchunk1Size)
    if debug == 1:
        print("VALID SUBCHUNK SIZE - \t\t", hex(Subchunk1Size))

    AudioFormat = int.from_bytes(data[8:10], byteorder='little')
    if AudioFormat != 0x00000001:
        close_program("ERROR 6: Invalid Audio Format",name, AudioFormat)
    if debug == 1:
        print("VALID AUDIO FORMAT - \t\t", hex(AudioFormat))

    SampleRate = int.from_bytes(data[12:16], byteorder='little')
    if SampleRate != 7575:
        close_program("ERROR 8: Invalid Sample Rate",name, SampleRate)
    if debug == 1:
        print("VALID SAMPLE RATE - \t\t", SampleRate)
        
    ByteRate = int.from_bytes(data[16:20], byteorder='little')
    BlockAlign = int.from_bytes(data[20:22], byteorder='little')

    BitsPerSample = int.from_bytes(data[22:24], byteorder='little')
    if BitsPerSample != 0X00000010:
        close_program("ERROR 9: Unexpected Bits per Sample",name, BitsPerSample)
    if debug == 1:
        print("VALID BITS PER SAMPLE - \t", hex(BitsPerSample))

    data = data[24:len(data)]

    chunkName = int.from_bytes(data[0:4], byteorder='big')
    if chunkName != 0x64617461: #Hex representation of "data"
        close_program("ERROR 10: Invalid Chunkname",name,chunkName)
    if debug == 1:
        print("VALID CHUNKNAME - \t\t", hex(chunkName))
        
    datalength = int.from_bytes(data[4:8], byteorder='little')
#    print("Data Length = ", hex(datalength), " - ", datalength, " bytes")

    payload = data[8:len(data)]

    #Repeat last byte if needed to ensure an Even number of bytes
    if len(payload)%2 == 1:
        payload.append(payload,payload[len(payload -1)])

    wav_data = to_array16(payload)
#    if len(wav_data)&2 != 0:
#        wav_data = wav_data[:len(wav_data)-1]

    return wav_data

#Based on the work found here https://www.cs.columbia.edu/~hgs/audio/dvi/
#indextable = [-1,-1,-1,-1,2,4,6,8,-1,-1,-1,-1,2,4,6,8]
stepsizetable = [7,8,9,10,11,12,13,14,16,17,19,21,23,25,28,31,34,37,41,45,50,55,60,66,73,80,88,97,107,118,130,145,157,173,190,209,230,253,279,307,337,371,408,449,494,544,598,658,724,796,876,963,1060,1166,1282,1411,1552,1707,1878,2066,2272,2499,2749,3024, 3327,3660,4026,4428,4871,5358,5894,6484,7132,7845,8630,9493,10442,11487,12635,13899,15289,16818,18500,20350,22385,24623,27086,29794,32767]
indextable = [-1,-1,-1,-1,2,4,6,8,-1,-1,-1,-1,2,4,6,8]
#indextable = [-1,-1,-1,-1,2,4,6,8]
#stepsizetable = [16, 17, 19, 21, 23, 25, 28, 31, 34, 37,41, 45, 50, 55, 60, 66, 73, 80, 88, 97,107, 118, 130, 143, 157, 173, 190, 209, 230, 253,279, 307, 337, 371, 408, 449, 494, 544, 598, 658,724, 796, 876, 963, 1060, 1166, 1282, 1411, 1552]

def compress_sample(table):
    length = len(table)
    predicted_sample = 0
    index = 0
    stepsize = stepsizetable[0]
    newsample = 0
    difference = 0
    finalsample = 0
    final_index = 0
    newtable = bytearray(length>>2)
    print("Now compressing file...")
#    time.sleep(0.3)

    #Go through the whole file
    for i in range(0,length,2):
        #First, snag 16-Bit Sample from Source file
        original_sample = int.from_bytes(table[i:i+2], byteorder='big',signed = "false")
        original_sample += 0xFFFF>>1 #(stepsizetable[len(stepsizetable)-1])-1
        original_sample >>= 3 #Algo uses 12-bit Input

        difference = original_sample - predicted_sample #Find difference from predicted sample
        if difference >= 0: #Set Sign Bit and find absolute value of difference
            newsample = 0
        else:
            newsample = 8
            difference = -difference
        mask = 4
        tempstepsize = stepsize
        for k in range(0,3,1):
            if (difference >= tempstepsize):
                newsample |= mask
                difference -= tempstepsize
            tempstepsize >>= 1
            mask >>= 1
        #Store 4-Bit Newsample
        if (i & 2):
            finalsample = finalsample << 4
            finalsample += newsample
#            finalsample = finalsample << 4
#            finalsample += newsample
            newtable[final_index] = finalsample
#            print("Final Byte = ", hex(finalsample)," - ", bin(finalsample))
            final_index += 1
            finalsample = 0
        else:
            finalsample += newsample

        #Compute New_Sample estimate using predicted_Sample
        difference = 0
        if (newsample & 4):
            difference += stepsize
        if (newsample & 2):
            difference += stepsize>>1
        if (newsample & 1):
            difference += stepsize>>2
        difference += stepsize>>3
        if (newsample & 8):
            difference = -difference

        predicted_sample += difference
        if (predicted_sample > stepsizetable[len(stepsizetable)-1]):
            predicted_sample = stepsizetable[len(stepsizetable)-1]
        elif (predicted_sample < -stepsizetable[len(stepsizetable)-1]-1):
            predicted_sample = -stepsizetable[len(stepsizetable)-1]-1

        #Compute new Stepsize
        index += indextable[newsample]
#        index += indextable[newsample & 0x07]
        if (index < 0):
            index = 0
        elif (index > len(stepsizetable)-1):
            index = len(stepsizetable)-1
        stepsize = stepsizetable[index]

    print("COMPRESSED LENGTH = ", hex(len(newtable)), " - ", len(newtable), " Bytes")
    return newtable


#-------------------- PARSE INPUT --------------------
pcmnames = evaluate_input_wavs()
out_names = return_outnames()
#Keep important information for when we generate an OKI Sample ROM
compressed_data = {}
compressed_lengths = {}
compressed_offsets = {}
for i in range(0,len(pcmnames),1):
    compressed_data.update({i : {}})
    compressed_lengths.update({i : 0})
    compressed_offsets.update({i : 0})

#print("PCNAMES")
#print(pcmnames)
time.sleep(2)


#-------------------- COMPRESS DATA --------------------
for z in range(0,len(pcmnames),1):
    with open(pcmnames[z], "rb") as input:
        size = os.path.getsize(pcmnames[z])
        tempfile = bytearray()
        tempfile = input.read(size)
        tempfile2 = bytearray(size)
        adpcm = bytearray(size)
        print(pcmnames[z], " - Size = ", hex(size), " - ", size, " Bytes")
        pcm_data = format_PCM(tempfile,pcmnames[z])
#        adpcm = compress_sample(pcm_data)
        compressed_data[z] = compress_sample(pcm_data)

    #Write the flipped data to a new file
    with open(out_names[z], "wb") as out:
        print("Writing - ", out_names[z], " -")
        time.sleep(1)
#        out.write(bytes(adpcm))
        out.write(bytes(compressed_data[z]))
        print("FINISHED COMPRESSING - ", pcmnames[z])


#-------------------- GENERATE AN OKI ROM BASED ON COMPRESSED DATA --------------------
print("Now writing OKI ROM...")
OKI_NAME = "sf2_18.11c" #Named after the one used by SF2 for testing purposes
OKI_LENGTH = 0x20000
OKI_Pointer_section_length = 0x400 #Data set aside for Pointer data, actual Sample data starts after this
#OKI_ROM = bytearray(OKI_LENGTH)
OKI_ROM = bytearray([0xff]*OKI_LENGTH)
OKI_ROM[0:8] = 0x0000000000000000.to_bytes(8,"big") #Ensures first Pointers are blank

sample_pointer_start = OKI_Pointer_section_length #Value containing Pointer to Sample data
sample_pointer_end = 0
sample_pointer_curosr = 8 #Starts at 8 so the first Sample is left blank
sample_data_curosr = sample_pointer_start

for i in range(0,len(pcmnames),1):
    #Sample data is fairly straightforwsrd, comprising of 2 empty Bytes, and 3 bytes apiece
    #denoting the Start and Endpoint of a given sample respectively
#Write Sample Pointers to ROM
#Write Start Pointer
    OKI_ROM[sample_pointer_curosr:sample_pointer_curosr+3] = sample_pointer_start.to_bytes(3,"big")
    sample_pointer_end = sample_pointer_start+ len(compressed_data[i]) #Ensures ending Pointer never overlaps
    sample_pointer_start = sample_pointer_end+1  #Ensure no data overlap
#Write End Pointer
    sample_pointer_curosr += 3
    OKI_ROM[sample_pointer_curosr:sample_pointer_curosr+3] = sample_pointer_end.to_bytes(3,"big")
    sample_pointer_curosr += 3
    OKI_ROM[sample_pointer_curosr:sample_pointer_curosr+2] = 0x0000.to_bytes(2,"big") #Set ramaining bytes to 0x00
    sample_pointer_curosr += 2 #Last 2 bytes are empty so ignore them

#Write Sample data to ROM
    OKI_ROM[sample_data_curosr:sample_data_curosr+ len(compressed_data[i])] = compressed_data[i]
    sample_data_curosr += len(compressed_data[i])
#    print(OKI_ROM)

#Pad the rest of Pointer data with 0xFF
#if sample_pointer_curosr < OKI_Pointer_section_length:
#    remainder = OKI_Pointer_section_length-sample_pointer_curosr
#    for i in range(sample_pointer_curosr,OKI_Pointer_section_length,4):
#        OKI_ROM[i:i+4] = 0xFFFFFFFF.to_bytes(4,"big")

with open(OKI_NAME,"wb") as out:
    out.write(bytes(OKI_ROM))

totalspace = 0
#Display Sample info
for i in range(0,len(pcmnames),1):
    printname = pcmnames[i].replace(input_path,"- ",1)
    printstr = str("{} - {} - {} - bytes ").format(printname,hex(len(compressed_data[i])),len(compressed_data[i]))
    totalspace += len(compressed_data[i])
    print(printstr)
remainder = OKI_LENGTH-totalspace
print(str("TOTAL SPACE USED = {} of {} - {}/{} - {}/{} bytes remaining").format(totalspace,OKI_LENGTH,hex(totalspace),hex(OKI_LENGTH),hex(remainder),remainder))

print(str("TOTAL SAMPLES USED = {} of {}").format(len(pcmnames),(OKI_Pointer_section_length>>2)-1))

