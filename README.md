# lmia assembler

## How to use

Give the path to the file that sould be assembled and it outputs the assembled instructions.
```bash
python3 assembler.py input_file_name
```

<br/>

## Examples
### Example 1
Input:
``` asm
main:
    ; add value from address 0xAB to register 2
    add r2, 0xAB
```
Output:
```
00: 28AB
```

<br/>

### Example 2
Input:
``` asm
; define constants!
$address1 = 0xA3
$address2 = 0xA4

main:
    ldr r0, $address1       ; load data from $address1 to register 0
    str r0, $address2       ; write data from register 0 to $address2
```
Output:
```
00: 00A3
01: 10A4
```

<br/>


### Example 3
Input:
``` assembly
$result = 0xE0
$value1 = 0xE1
$value2 = 0xE2

; copy the largest of $value1 and $value2 to $result

start:
    ldr r0, $value1         ; load value from address $value1
    sub r0, $value2         ; subtract with value at address $value2

    bge load1               ; jump to load1 if $value1 was greater or equal to $value2
    ; if no jump was made, fall through to load2

load2:
    ldr r1, $value2         ; load value from address $value2
    bra save                ; jump to save

load1:
    ldr r1, $value1         ; load value from address $value2
    ; fall through to save

save:
    str r1, $result         ; store the value at address $result
    halt
```
Output:
```
00: 00E1
01: 30E2
02: A002
03: 04E2
04: 6001
05: 04E1
06: 14E0
07: 8000
```
