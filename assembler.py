# Unformatted command dictionary.
com = {'0': '0101010',
        '1': '0111111',
        '-1': '0111010',
        'D': '0001100',
        '{0}': '{0}110000',
        '!D': '0001101',
        '!{0}': '{0}110001',
        '-D': '0001111',
        '-{0}': '{0}110011',
        'D+1': '0011111',
        '{0}+1': '{0}110111',
        'D-1': '0001110',
        '{0}-1': '{0}110010',
        'D+{0}': '{0}000010',
        'D-{0}': '{0}010011',
        '{0}-D': '{0}000111',
        'D&{0}': '{0}000000',
        'D|{0}': '{0}010101',
        'JGT': '001',
        'JEQ': '010',
        'JGE': '011',
        'JLT': '100',
        'JNE': '101',
        'JLE': '110',
        'JMP': '111',
		'': '000'}

# Destination dictionary
dst = {'M': '001',
        'D': '010',
        'MD': '011',
        'A': '100',
        'AM': '101',
        'AD': '110',
        'AMD': '111',
		'': '000'}

# Reserved memory dictionary
mem = {'SP': '0',
        'LCL': '1',
        'ARG': '2',
        'THIS': '3',
        'THAT': '4',
        'SCREEN': '16384',
        'KBD': '24576'}

# Formats command dict. with A and M differentiation
temdic = com
for item in list(com):
    temit = item
    if "{" in item:
        temdic[temit.format('A')] = temdic[item].format('0')
        temdic[temit.format('M')] = temdic[item].format('1')
        del temdic[item]
com = temdic

# Adds R0-15 addresses to memory dict.
for i in range(16):
    mem['R' + str(i)] = i

# Main method, takes file and passes it to assembler.
def main(asm):
    with open(asm, 'r') as f:
        raw = []
        # Reads whitespace-removed file into array of lines
        lines = f.read().replace("\s", "").splitlines()
        for line in lines:
            # Removes comments
            line = line.split("//")[0]
            # Does not include empty lines
            if line == "":
                continue
            raw.append(line)
        Assemble(raw, asm.split('.')[0])

def Assemble(lines, name):

    from string import Template
    # This function uses templates to generate formatted instructions
    a = Template('0$addr')
    d = Template('111$instr$dest$jmp')
    commands = []
    newmem = 16
    ROM = 0

    # First passthrough; adds all pseudo-symbols to memory
    for i in lines:
        sym = i
        if sym[0] == "(":
            sym = sym[1:(len(sym)-1)]
            mem[sym] = ROM
            continue
        ROM += 1

    #Second passthrough; fully assembles code and writes to .hack file.
    for j in lines:
        command = j
        # Handles address compilation
        if command[0] == "@":
            toBinary = lambda s: bin(int(s))[2:].zfill(15)
            command = command[1:]
            if command not in mem and not command.isdecimal():
                mem[command] = str(newmem)
                newmem += 1
            if command in mem:
                command = mem[command]
            command = toBinary(command)
            command = a.substitute(addr=command)
            commands.append(command)
        # Handles instruction compilation
        elif command[0] != "(":
            # Makes (I, ';', J) tuplet, or (I, '', '') if no jmp
            ij = command.partition(';')
            # Makes (D, '=', I) tuplet, or ('','', I) if no dest
            di = ij[0].rpartition('=')
            idj = [di[2], di[0], ij[2]]
            command = d.substitute(instr=com[idj[0]], dest=dst[idj[1]], jmp=com[idj[2]])
            commands.append(command)

    # Writes all lines to .hack file
    with open(name + '.hack', 'w') as f:
        for item in commands:
            f.write(item + '\n')

# Needed for command line support
if __name__ == "__main__":
    import sys
    main(sys.argv[1])
