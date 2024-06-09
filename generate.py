from __future__ import annotations
from datetime import date


VOCALS = ['A', 'E', 'I', 'O', 'U']
MONTH_DECODE_TABLE = ['A', 'B', 'C', 'D', 'E', 'H', 'L', 'M', 'P', 'R', 'S', 'T']

CONTROL_CODE_EVEN_DECODE_TABLE = {chr(0x30 + key): key for key in range(10)}
CONTROL_CODE_EVEN_DECODE_TABLE.update({chr(0x41 + key): key for key in range(26)})

CONTROL_CODE_ODD_DECODE_TABLE = {
    '0': 1,
    '1': 0,
    '2': 5,
    '3': 7,
    '4': 9,
    '5': 13,
    '6': 15,
    '7': 17,
    '8': 19,
    '9': 21,
    'A': 1,
    'B': 0,
    'C': 5,
    'D': 8,
    'E': 9,
    'F': 13,
    'G': 15,
    'H': 17,
    'I': 19,
    'J': 21,
    'K': 2,
    'L': 4,
    'M': 18,
    'N': 20,
    'O': 11,
    'P': 3,
    'Q': 6,
    'R': 8,
    'S': 12,
    'T': 14,
    'U': 16,
    'V': 10,
    'W': 22,
    'X': 25,
    'Y': 24,
    'Z': 23
}


def load_province_decode_table() -> dict[str, str]:
    return {'PT': 'G713'}


def generate_fiscal_code(name: str, surname: str, sex: str, birth_day: date, province: str):
    name = name.upper()
    surname = surname.upper()
    sex = sex.upper()
    province = province.upper()

    surname_part = ''
    idx = 0
    while idx < len(surname) and len(surname_part) < 3:
        if surname[idx] not in VOCALS:
            surname_part += surname[idx]
        idx += 1
    idx = 0
    while idx < len(surname) and len(surname_part) < 3:
        if surname[idx] in VOCALS:
            surname_part += surname[idx]
        idx += 1
    surname_part.rjust(3, 'X')

    consonants = []
    name_part = ''
    idx = 0
    while idx < len(name):
        if name[idx] not in VOCALS:
            consonants.append(name[idx])
        idx += 1
    if len(consonants) > 3:
        name_part = consonants[0] + consonants[2] + consonants[3]
    else:
        name_part = ''.join(consonants)

    idx = 0
    while idx < len(name) and len(name_part) < 3:
        if name[idx] in VOCALS:
            name_part += name[idx]
        idx += 1
    name_part.rjust(3, 'X')

    year = str(birth_day.year)[-2:]
    month = MONTH_DECODE_TABLE[birth_day.month - 1]
    day_and_sex = str(birth_day.day + 0 if sex == 'M' else 40).ljust(2, '0')

    province_decode_table = load_province_decode_table()
    province_code = province_decode_table[province]

    fiscal_code = surname_part + name_part + year + month + day_and_sex + province_code

    # since position 1 corresponds to the first character (instead of the second), odd and even are swapped
    odd_sum = sum([CONTROL_CODE_ODD_DECODE_TABLE[fiscal_code[i]] for i in range(len(fiscal_code)) if i % 2 == 0])
    even_sum = sum([CONTROL_CODE_EVEN_DECODE_TABLE[fiscal_code[i]] for i in range(len(fiscal_code)) if i % 2 == 1])

    control_code = chr(0x41 + ((odd_sum + even_sum) % 26))

    return fiscal_code + control_code


def main() -> int:
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
