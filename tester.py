import os
import assembler


def run_test(path: str):
    input_lines = open(path + '/input', "r").readlines()
    expected_output_lines = open(path + '/output', "r").read().splitlines()

    assembled = assembler.assemble(input_lines)

    success = expected_output_lines == assembled

    if not success:
        print('Fail!')
        print('Expected:')
        for line in expected_output_lines:
            print(line)
        print('Actual')
        for line in assembled:
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
