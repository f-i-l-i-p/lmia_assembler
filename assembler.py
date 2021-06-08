#!/usr/bin/env python3

from typing import List, Dict, NamedTuple
import re


class Operation(NamedTuple):
    code: int
    relative_address: bool = False


OP_CODES = {
    'ldr': Operation(code=0x0),
    'str': Operation(code=0x1),
    'add': Operation(code=0x2),
    'sub': Operation(code=0x3),
    'and': Operation(code=0x4),
    'lsr': Operation(code=0x5),
    'bra': Operation(code=0x6, relative_address=True),
    'bne': Operation(code=0x7, relative_address=True),
    'halt': Operation(code=0x8),
    'cmp': Operation(code=0x9),
    'bge': Operation(code=0xA, relative_address=True),
    'beq': Operation(code=0xB, relative_address=True)
}


# ============================================================================
# Matching
# ===========================================================================

NAME = '(([A-Za-ln-qs-z0-9_-][A-Za-z0-9_-]*)|[A-Za-z0-9_-]|([A-Za-z0-9_-][A-Za-z0-9_-]+))'
VARIABLE = '(\$[A-Za-z0-9_-]+)'
HEX = '(0x[a-fA-F0-9]+)'
OPERATION = '([A-Za-z]+)'
REGISTER = '(r[0-9])'
MODE = '(m[0-9])'


# Variables

def is_variable_init(line: str) -> bool:
    # Example match: const hello = 0x3B
    return re.match(f'{VARIABLE} = {HEX}', line) is not None


def get_variable_name(line: str) -> str:
    return line.split(' ')[0]


def get_variable_value(line: str) -> int:
    value = line.split(' ')[2]
    return int(value, base=16)


# Subroutines

def is_subroutine_name(line: str) -> bool:
    # Example match: subroutine:
    n = re.match(f'{NAME}:', line) is not None
    return n


def get_subroutine_name(line: str) -> bool:
    return line.split(' ')[0][:-1]


# Instructions

def is_instruction(line: str) -> bool:
    # Example match: ADD r0, 0xA5
    # Example match: ADD r0, hello
    if is_subroutine_name(line) or is_variable_init(line):
        return False
    return re.match(f'{OPERATION}( {REGISTER},?)?( {MODE},?)?( ({HEX}|{VARIABLE}|{NAME}))?', line) is not None


def get_instruction_operation(line: str) -> str:
    return line.split(' ')[0]


def get_instruction_register(line: str) -> str:
    # returns 0 if no register found
    if not re.match(f'{OPERATION} {REGISTER}', line):
        return '0'
    else:
        return line.split(' r')[1][0]


def get_instruction_mode(line: str) -> str:
    # returns 0 if no mode found
    if not re.match(f'{OPERATION}( {REGISTER},?)? {MODE}', line):
        return '0'
    else:
        return line.split(' m')[1][0]


def get_instruction_value(line: str) -> str:
    # returns 0x0 if no value found
    splits = line.split(' ')
    if len(splits) >= 2 and re.match(f'{HEX}|{VARIABLE}|{NAME}', splits[-1]):
        return splits[-1]
    else:
        return '0x0'


# Format

def format_line(line: str) -> str:
    # Remove comment
    new_line = line.split(';')[0]
    # Strip empty characters
    new_line = new_line.strip()

    return new_line


# ===========================================================================
# Parsing
# ===========================================================================

def parse_instruction(line_count: int, instruction_count: int, line: str,
                      symbols: Dict[str, int], op_codes: Dict[str, Operation]) -> int:
    """
    Converts an instruction to bits
    """
    op_str = get_instruction_operation(line)
    r_str = get_instruction_register(line)
    m_str = get_instruction_mode(line)
    v_str = get_instruction_value(line)

    # Op code
    if op_str not in op_codes:
        raise SyntaxError(
            f'Syntax error in line {line_count}. The operation {op_str} is not a valid operation.')
    op = op_codes[op_str]

    # Register
    r = int(r_str, base=16)

    # Mode
    m = int(m_str, base=16)

    # Value
    if re.match('0x', v_str):
        v = int(v_str, base=16)
    else:
        if v_str not in symbols:
            raise SyntaxError(
                f'Syntax error in line {line_count}. The value {v_str} has not been defined.')
        v = symbols[v_str]

        if op.relative_address:
            v = calculate_relative_address_jump(instruction_count, v)

    return op.code * 2**12 + r * 2**10 + m * 2**8 + v


def calculate_relative_address_jump(instruction_count: int, destination_address: int) -> int:
    return destination_address - instruction_count - 1


# ===========================================================================
# Assembling
# ===========================================================================

def construct_symbol_table(line_count: int, instruction_count: int, lines: List[str],
                           symbols: Dict[str, int]) -> Dict[str, int]:
    """
    First pass in the assembling.
    Stores all constants and subroutine addressses in the symbols table.
    """
    new_symbols = symbols.copy()

    if len(lines) == 0:
        return new_symbols

    line = format_line(lines[0])

    # If variable
    if is_variable_init(line):
        name = get_variable_name(line)

        if name not in new_symbols:
            new_symbols[name] = get_variable_value(line)
        else:
            raise SyntaxError(
                f'Syntax error in line {line_count}. {name} has already been defined.')

    # If subroutine
    elif is_subroutine_name(line):
        name = get_subroutine_name(line)

        if name not in new_symbols:
            new_symbols[name] = instruction_count
        else:
            raise SyntaxError(
                f'Syntax error in line {line_count}. {name} has already been defined.')

    # If instruction
    elif is_instruction(line):
        instruction_count += 1

    # Not empty line
    elif line:
        raise SyntaxError(f'Syntax error in line {line_count}.\n{line}')

    return construct_symbol_table(line_count + 1, instruction_count, lines[1:], new_symbols)


def convert_to_bits(line_count: int, instruction_count: int, lines: List[str],
                    symbols: Dict[str, int], op_codes: Dict[str, Operation],
                    compiled: List[int]) -> List[int]:
    """
    Second pass in the assembling.
    Converts all instructions to numbers.
    """
    if len(lines) == 0:
        return compiled

    line = format_line(lines[0])

    # If instruction
    if is_instruction(line):
        bits = parse_instruction(
            line_count, instruction_count, line, symbols, op_codes)
        line_count += 1
        instruction_count += 1
        return convert_to_bits(line_count, instruction_count, lines[1:], symbols, op_codes, compiled + [bits])

    # If variable or subroutine
    elif is_subroutine_name(line) or is_variable_init(line):
        line_count += 1

    # Not empty line
    elif line:
        raise SyntaxError(f'Syntax error in line {line_count}.\n{line}')

    return convert_to_bits(line_count + 1, instruction_count, lines[1:], symbols, op_codes, compiled)


def assemble(lines: List[str], line_numbers: bool = True) -> List[str]:
    """
    Assembles a list of strings.
    """
    symbols = construct_symbol_table(0, 0, lines, dict())

    bits = convert_to_bits(0, 0, lines, symbols, OP_CODES, list())

    if line_numbers:
        return [f'{hex(index)[2:].upper().zfill(2)}: {hex(line)[2:].upper().zfill(4)}' for index, line in enumerate(bits)]
    else:
        return [hex(index)[2:].upper().zfill(2) for line in bits]
