import sys
from typing import List, Dict

args = sys.argv[1:]

if (len(args) == 0):
    print("No arguments given. Specify the path to the file that should be assembled.")
    exit(0)
if (len(args) > 2):
    print("Too many arguments! Maximum is 2: Input file path, and Output file path.")
    exit(0)


def loadInputFile():
    filePath = args[0]
    print("Loading " + filePath)
    return open(filePath, "r")


def output(data: List[str]):
    useOutputFile = len(args) == 2

    # Write to file
    if useOutputFile:
        filePath = args[1]

        f = open(filePath, "w")
        f.writelines(data)
        f.close()

        print(f"Done! Written to {filePath}")

    # Print to terminal
    else:
        print("Done!\n")
        for line in data:
            print(line)


class Assembler:
    op_codes = {
        'LDR': 0x0,
        'STR': 0x1,
        'AND': 0x4,
        'LSR': 0x5,
        'BRA': 0x8,
    }
    registers = {
        'r0': 0x0,
        'r1': 0x1,
        'r2': 0x2,
        'r3': 0x3,
    }

    def __init__(self):
        # Dict for mapping jump tags to memory addresses
        self.jump_tags: Dict[str, int] = dict()

    def assemble(self, instructions: List[str]) -> List[str]:
        """
        Takes a list of instructions that should be assembled.
        Returns a list with assembled instructions.
        """
        cleaned_instructions = self.clean_instructions(instructions)

        self.map_jump_tags(cleaned_instructions)

        assembled = []

        for num, instr in enumerate(cleaned_instructions):
            assembled.append(self.assemble_instruction(num, instr))

        return assembled

    def clean_instructions(self, instructions: List[str]) -> List[str]:
        """
        Removes comments, removes empty instructions, and strips empty characters,
        """
        new_instructions = []

        for instr in instructions:
            # Remove comment
            instr = instr.split(';')[0]

            # Strip empty characters
            instr = instr.strip()

            # Only add non-empty instructions
            if instr:
                new_instructions.append(instr)

        return new_instructions

    def map_jump_tags(self, instructions: List[str]) -> None:
        """
        Maps the jump tags to their corresponding address.
        Also removes the jump tags from the instructions list.
        """
        self.jump_tags.clear()

        for num, instr in enumerate(instructions):
            # If jump tag
            if ':' in instr:
                name = instr.split(':')[0]
                self.jump_tags[name] = num

                instructions.remove(instr)


    def assemble_instruction(self, line_num: int, instruction: str) -> str:
        """
        Assembles a given instruction.
        """
        parts = instruction.split(', ')

        if len(parts) != 4:
            raise SyntaxError(
                f"Syntax error at line {line_num}:\n{instruction}")

        op_code = self.parse_op_code(parts[0])
        register = self.parse_register(parts[1])
        m = self.parse_m(parts[2])
        address = self.parse_address(parts[3], line_num)

        return f"{self.to_hex(op_code)}{self.to_hex(register + m)}{address}"

    def parse_op_code(self, op_code: str) -> int:
        """
        Returns op code as a decimal integer.
        """
        return self.op_codes[op_code]

    def parse_register(self, register: str) -> int:
        """
        Returns register nubmer as a decimal integer.
        """
        return self.registers[register]

    def parse_m(self, m: str) -> int:
        """
        Returns m as a decimal number.
        """
        if len(m) != 2:
            raise SyntaxError("m value should be two binary digits")

        return int(m[0]) * 2 + int(m[1]) * 1

    def parse_address(self, address: str, line_num: str) -> str:
        """
        Returns an address as a hex string.
        """
        length = 2  # Number of digits that the address should be

        # If jump tag
        if address.isidentifier():
            jump_address = self.jump_tags[address]

            # Convert to relative address because thats what lmia uses
            relative_address = jump_address - line_num - 1

            hex_str = self.to_hex(relative_address, length)

        # If hex address
        else:
            hex_str = address.split('x')[1]

            if len(hex_str) > length:
                raise SyntaxError("Address is too long.")

            hex_str = '0' * (length - len(hex_str)) + hex_str

        return hex_str

    def to_hex(self, num: int, length: int = 0) -> str:
        """
        Converts an integer to a hex string. length is the minimum number of hex-digits.
        """
        # Create hex and remove '0x'
        hex_str = hex(num).split('x')[1]
        # Add leading 0:s if too short
        hex_str = '0' * (length - len(hex_str)) + hex_str

        # Set first bit to 1 if num is negative
        if num < 0:
            # Convert to binary and remove 0b
            bin_str = bin(int(hex_str[0], 16))[2:]
            # Make sure it's 4 digits
            bin_str = '0' * (4 - len(bin_str)) + bin_str

            # Set first bit to 1
            bin_str = '1' + bin_str[1:]

            # Convert bin_str to hex and update hex_str
            hex_str = hex(int(bin_str, 2))[2:] + hex_str[1:]

        return hex_str


inputFile = loadInputFile()

assembler = Assembler()
assembled = assembler.assemble(inputFile.readlines())
output(assembled)

inputFile.close()
