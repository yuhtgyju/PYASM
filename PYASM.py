from sys import argv
import os

namespace = [
    "move", "screen", "clear", "string",
    "addprint", "subprint", "multprint", "divprint", "expoprint",
    "nln"
]

file = []
input_name = ""
output_name = ""

# Read lines from input .pyasm file
def readFile(filetoread: str):
    global file
    if os.path.isfile(filetoread):
        with open(filetoread, "r") as asmFile:
            file = asmFile.readlines()
    else:
        print("ERR: [1] Invalid File")
        exit(1)

# Write a list of byte values to the output file
def write_bytes(bytestr, output):
    output.write(bytes(bytestr))

# Append boot signature (0x55AA) for BIOS boot
def pad_and_finalize():
    with open(output_name, "ab") as output:
        current_size = output.tell()
        if current_size > 510:
            print("ERR: Output too large for boot sector")
            return
        output.write(b'\x00' * (510 - current_size))  # Pad to 510 bytes
        output.write(b'\x55\xAA')  # Boot signature


# Main compilation routine
def compile():
    with open(output_name, "wb") as output:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#//"):
                continue  # Skip empty lines or comments

            # Replace \ with space and split by commas first
            line = line.replace("\\", " ")
            tokens = ("".join(line.split(","))).split()
            if not tokens:
                continue

            cmd = tokens[0]

            if cmd not in namespace:
                print(f"ERR: [2] Unknown name: {cmd}")
                continue

            if cmd == "move":
                if len(tokens) < 3:
                    print("ERR: move expects 2 arguments")
                    continue
                src, dest = tokens[1], tokens[2]

                # Check if it's a character literal (e.g. ;A)
                if src.startswith(";") and len(src) == 2:
                    val = ord(src[1])
                else:
                    try:
                        val = int(src, 16) if src.startswith("0x") else int(src)
                    except ValueError:
                        print(f"Invalid immediate value: {src}")
                        continue

                reg_codes = {
                    "al": 0xB0,
                    "cl": 0xB1,
                    "dl": 0xB2,
                    "bl": 0xB3,
                    "ah": 0xB4,
                    "ch": 0xB5,
                    "dh": 0xB6,
                    "bh": 0xB7
                }
                opcode = reg_codes.get(dest.lower())
                if opcode is None:
                    print(f"Unknown register: {dest}")
                else:
                    write_bytes([opcode, val & 0xFF], output)

            elif cmd == "screen":
                write_bytes([0xB4, 0x0E, 0xCD, 0x10], output)

            elif cmd == "clear":
                write_bytes([
                    0xB4, 0x06,
                    0xB0, 0x00,
                    0xB7, 0x07,
                    0xB5, 0x00,
                    0xB1, 0x00,
                    0xBA, 0x4F, 0x18,
                    0xCD, 0x10
                ], output)
                write_bytes([
                    0xB4, 0x02,
                    0xB7, 0x00,
                    0xB6, 0x00,
                    0xB2, 0x00,
                    0xCD, 0x10
                ], output)

            elif cmd == "string":
                if len(tokens) < 3:
                    print("ERR: string expects 2+ arguments")
                    continue

                reg = tokens[-1]
                raw_str = " ".join(tokens[1:-1]).replace("\\", " ")

                reg_codes = {
                    "al": 0xB0,
                    "ah": 0xB4,
                    "bl": 0xB3,
                    "bh": 0xB7
                }

                opcode = reg_codes.get(reg.lower())
                if opcode is None:
                    print(f"Unknown register: {reg}")
                    continue

                for char in raw_str:
                    if char == "/":  # Newline!
                        for c in "\r\n":  # BIOS-style newline
                            output.write(bytes([opcode, ord(c)]))  # mov reg, c
                            output.write(bytes([0xB4, 0x0E]))       # mov ah, 0x0E
                            output.write(bytes([0xCD, 0x10]))       # int 10h
                    else:
                        output.write(bytes([opcode, ord(char)]))    # mov reg, char
                        output.write(bytes([0xB4, 0x0E]))           # mov ah, 0x0E
                        output.write(bytes([0xCD, 0x10]))           # int 10h
            
            elif cmd.endswith("print") and len(tokens) == 3:
                op = cmd[:-5]
                try:
                    a = int(tokens[1])
                    b = int(tokens[2])
                except ValueError:
                    print(f"ERR: Invalid arguments to {cmd}")
                    continue

                if op == "add":
                    result = a + b
                elif op == "sub":
                    result = a - b
                elif op == "mult":
                    result = a * b
                elif op == "div":
                    if b == 0:
                        print("ERR: Division by zero")
                        continue
                    result = a // b
                elif op == "expo":
                    result = a ** b
                else:
                    print(f"ERR: Unknown operation: {op}")
                    continue

                for ch in str(result):
                    output.write(bytes([0xB0, ord(ch)]))  # mov al, digit
                    output.write(bytes([0xB4, 0x0E]))     # mov ah, 0x0E
                    output.write(bytes([0xCD, 0x10]))     # int 10h
            elif cmd == "nln":
                for c in "\r\n":
                    val = ord(c)
                    output.write(bytes([0xB0, val]))  # mov al, val
                    output.write(bytes([0xB4, 0x0E])) # mov ah, 0x0E
                    output.write(bytes([0xCD, 0x10])) # int 10h

        write_bytes([0xEB, 0xFE], output)  # Infinite loop

    pad_and_finalize()

# Entry point
if __name__ == "__main__" and len(argv) == 3:
    input_name = argv[1]
    output_name = argv[2]
    if not input_name.endswith(".pyasm"):
        print("WARN: Non .pyasm file. May not be safe to compile.")
        input("Continue? ")
    readFile(input_name)
    compile()
else:
    print("Usage:\n  python3 PYASM.py <input.pyasm> <output.bin>")
