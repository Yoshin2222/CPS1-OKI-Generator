import os

print("----- OKI ROM SAMPLE EXTRACTOR ------")
print("Enter name of OKI ROM to extract Samples from...")
input_path = input()

while not os.path.exists(input_path):
    msg = str("-{}- doesn't ecist, try something else!".format(input_path))
    print(msg)
    input_path = input()

#Once a file is loaded, grab important data before extracting
file_size = os.path.getsize(input_path)
sample_pointer_section = 0x400
sp_cursor_start = 8 #Skip the first 8 bytes as they're always blank
sample_pointer_cursor = sp_cursor_start

#Create a temporary copy of the ROM
with open(input_path, "rb") as input:
    OKI_ROM = input.read(file_size)

sample_start_pointers = {} #Keep a list of where every sample begins in ROM
sample_end_pointers = {} #Keep a list of where every sample ends in ROM

#Gather Pointer data
for index in range(0,sample_pointer_section,8):
    if int.from_bytes(OKI_ROM[sample_pointer_cursor:sample_pointer_cursor+8],"big") != 0xFFFFFFFFFFFFFFFF: #Invalid
        #First grab Start Pointer (first 3 Bytes since the OKI uses 24-bit addresses
        pointer = int.from_bytes(OKI_ROM[sample_pointer_cursor:sample_pointer_cursor+3],"big")
        sample_start_pointers.update({index>>3 : pointer})
        sample_pointer_cursor += 3
        #Grab End Pointer
        pointer = int.from_bytes(OKI_ROM[sample_pointer_cursor:sample_pointer_cursor+3],"big")
        sample_end_pointers.update({index>>3 : pointer})
        sample_pointer_cursor += 5 #Move to the next Pointer
#print(sample_start_pointers)

#With this pointer data, isolate each Sample, and write it to a new folder!
sample_path = "OKI_OUT"
while not os.path.exists(sample_path):
    os.makedirs(sample_path)
sample_data = {}

for i in range(0,len(sample_start_pointers),1):
        if len(OKI_ROM[sample_start_pointers[i]:sample_end_pointers[i]]) != 0: #Ensure not invalid
            smp = str("{} - {} - {}-{} = {}-{}").format(input_path,"SMPL", i,hex(i),hex(sample_start_pointers[i]),hex(sample_end_pointers[i]))
            sample_data.update({i : OKI_ROM[sample_start_pointers[i]:sample_end_pointers[i]]})
            with open(os.path.join(sample_path, smp),"wb") as out:
                out.write(bytes(sample_data[i]))

