# lmia_assembler

**Output to terminal**
```bash
$ python3 lmia_assembler.py input_file_name
```
**Output to file**
```bash
$ python3 lmia_assembler.py input_file_name output_file_name
```

### Example code
```
main:
    LDR, r1, m0, 0x10  ; load register 1 from 0x10

loop:
    ; duplicate value in 0x10
    ADD, r1, m0, 0x10
    STR, r1, m0, 0x10

    BRA, na, na, loop  ; loop
```
