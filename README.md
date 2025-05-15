# PYASM Compiler

PYASM is a minimalistic Python-based assembler that compiles a small custom assembly-like language into a bootable x86 binary. The output is a boot sector image usable in virtual machines like QEMU or real hardware (if you're brave).

## Features

### Register Movement
Move an immediate value or character into a register:

```
move <value> <reg>
```

### Screen Setup
Initialize BIOS teletype output:

```
screen
```

### Clear Screen
Clears the text display using BIOS interrupt 10h:

```
clear
```

### String Output
Outputs a string using BIOS teletype (int 10h), supports `/` for newline:

```
string Hello, World! al
```

### Math Print Operations
Supports immediate math operations and prints the result:

- Addition:
  ```
  addprint <a> <b>
  ```

- Subtraction:
  ```
  subprint <a> <b>
  ```

- Multiplication:
  ```
  multprint <a> <b>
  ```

- Division (integer):
  ```
  divprint <a> <b>
  ```

- Exponentiation:
  ```
  expoprint <a> <b>
  ```

### Newline
Outputs a BIOS-style newline (CR + LF):

```
nln
```

## Syntax Notes

- Immediate values can be:
  - Decimal numbers (e.g. `10`)
  - Hex numbers (e.g. `0x1A`)
  - Character literals prefixed with `;` (e.g. `;A`)
- Comments are marked with `#//` and are ignored.
- Lines are space or comma separated. `\` is replaced with a space.

## Usage

```bash
python3 PYASM.py <input.pyasm> <output.bin>
```

Example:

```bash
python3 PYASM.py hello.pyasm hello.bin
```

- If the file extension is not `.pyasm`, you'll get a warning prompt.

## Boot Sector Details

- Final binary is padded to 512 bytes.
- The last two bytes are the required BIOS signature: `0x55AA`.
- An infinite loop (`jmp $`) is inserted at the end of the program to halt execution.

## Error Handling

- Invalid commands produce `ERR` messages.
- Division by zero is handled.
- Output files exceeding 510 bytes (before boot signature) will abort compilation.

## Supported Registers

For the `move` and `string` commands:

```
al, cl, dl, bl, ah, ch, dh, bh
```

## Sample `.pyasm` File

```pyasm
clear
string Hello,/World! al
nln
addprint 4 5
nln
move ;X al
screen
```

## License

No license. Do whatever you want with it.
