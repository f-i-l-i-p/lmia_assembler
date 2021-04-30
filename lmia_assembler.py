import sys
from typing import List

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
    }
    registers = {
        'r0': 0x0,
        'r1': 0x1,
        'r2': 0x2,
        'r3': 0x3,
    }

    def assemble(self, instructions: List[str]) -> List[str]:
        """
        Takes a list of instructions that should be assembled.
        Returns a list with assembled instructions.
        """
        assembled = []

        for num, instr in enumerate(instructions):
            striped_instr = instr.rstrip()

            # Skip if empty instruction
            if not striped_instr:
                continue

            assembled.append(self.assemble_instruction(num, striped_instr))

        return assembled

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
        address = self.parse_address(parts[3])

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

    def parse_address(self, address: str) -> str:
        """
        Returns an address as a hex string.
        """
        return address.split('x')[1][:2]

    def to_hex(self, num: int) -> str:
        """
        Converts an integer to a hex string.
        """
        return hex(num).split('x')[1]


inputFile = loadInputFile()

assembler = Assembler()
assembled = assembler.assemble(inputFile.readlines())
output(assembled)

inputFile.close()
