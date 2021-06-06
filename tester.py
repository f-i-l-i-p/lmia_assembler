import os
from lmia_assembler import Assembler


def run_test(path: str):
    input_lines = open(path + '/input', "r").readlines()
    expected_output_lines = open(path + '/output', "r").readlines()

    assembler = Assembler()
    assembled = assembler.assemble(input_lines)

    # Add line numbers
    data_with_line_numbers = []
    for num, line in enumerate(assembled):
        hex_str = hex(num)[2:]
        hex_str = '0' * (2 - len(hex_str)) + hex_str
        data_with_line_numbers.append(f"{hex_str}: {line}")

    success = expected_output_lines == data_with_line_numbers

    if not success:
        print('Fail!')
        print('Expected:')
        for line in expected_output_lines:
            print(line)
        print('Actual')
        for line in data_with_line_numbers:
            print(line)

    return success


def run_tests():
    dirs = [
        f'tests/{d}' for d in os.listdir('tests')
        if os.path.isdir(f'tests/{d}')
    ]

    passed = 0
    for dir in dirs:
        success = run_test(os.path.realpath(dir))

        if success:
            passed += 1

    print(f'Passed {passed}/{len(dirs)} tests.')


if __name__ == '__main__':
    run_tests()
