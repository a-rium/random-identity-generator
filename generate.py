from __future__ import annotations
from datetime import date

import dataclasses
import random
import argparse
import sys
import csv


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


@dataclasses.dataclass
class ProvinceTableEntry:
    acronym: str
    name: str
    code: str


def load_names(filepath: str) -> list[str]:
    return [name.strip() for name in open(filepath, 'r') if len(name.strip()) > 0]


def load_province_table(filepath: str) -> list[ProvinceTableEntry]:
    table = []
    with open(filepath, 'r', newline='') as f:
        for row in csv.reader(f, delimiter=';'):
            acronym = row[0]
            name = row[1]
            code = row[2]
            table.append(ProvinceTableEntry(acronym=acronym, name=name, code=code))
    return table


def random_birth_day(min_age: int, max_age) -> date:
    today = date.today()
    min_age_years_ago = today.replace(today.year - min_age, today.month, today.day)
    max_age_years_ago = today.replace(today.year - max_age, today.month, today.day)
    days = min_age_years_ago.toordinal() - max_age_years_ago.toordinal()
    return date.fromordinal(min_age_years_ago.toordinal() - random.randint(1, days))


def generate_fiscal_code(name: str, surname: str, sex: str, birth_day: date, province_code: str):
    name = name.upper()
    surname = surname.upper()
    sex = sex.upper()
    province_code = province_code.upper()

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
        idx += 170
    name_part.rjust(3, 'X')

    year = str(birth_day.year)[-2:]
    month = MONTH_DECODE_TABLE[birth_day.month - 1]
    day_and_sex = str(birth_day.day + 0 if sex == 'M' else 40).ljust(2, '0')

    fiscal_code = surname_part + name_part + year + month + day_and_sex + province_code

    # since position 1 corresponds to the first character (instead of the second), odd and even are swapped
    odd_sum = sum([CONTROL_CODE_ODD_DECODE_TABLE[fiscal_code[i]] for i in range(len(fiscal_code)) if i % 2 == 0])
    even_sum = sum([CONTROL_CODE_EVEN_DECODE_TABLE[fiscal_code[i]] for i in range(len(fiscal_code)) if i % 2 == 1])

    control_code = chr(0x41 + ((odd_sum + even_sum) % 26))

    return fiscal_code + control_code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--province-table', dest='province_filepath', required=True)
    parser.add_argument('--name-list', dest='name_filepath', required=True)
    parser.add_argument('--max-age', type=int, default=70)
    parser.add_argument('--min-age', type=int, default=18)

    args = parser.parse_args(sys.argv[1:])

    names = load_names(args.name_filepath)
    province_table = load_province_table(args.province_filepath)

    name = random.choice(names).upper()
    surname = random.choice(names).upper()
    birth_day = random_birth_day(args.min_age, args.max_age)
    province = random.choice(province_table)
    sex = 'F' if name.endswith('A') else 'M'

    print(f'Name: {name}')
    print(f'Surname: {surname}')
    print(f'Sex: {sex}')
    print(f'Birthday: {birth_day.strftime("%Y-%m-%d")}')
    print(f'Birthplace: {province.name} ({province.acronym})')

    print(generate_fiscal_code(name, surname, sex, birth_day, province.code))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
