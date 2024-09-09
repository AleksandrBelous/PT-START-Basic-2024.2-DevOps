import random
import re
import logging
import datetime

# logging.disable(logging.CRITICAL)
logging.basicConfig(filename=f'task-1-3-log-{datetime.datetime.now()}.txt', level=logging.DEBUG,
                    format=' %(asctime)s - %(levelname)s - %(message)s'
                    )


def create_err_file(filename: str):
    separators = [",", ";", "."]
    with open(filename, "w") as f:
        for _ in range(10000):
            line_length = random.randint(1, 100)
            line = ""
            for _ in range(line_length):
                char = str(random.randint(-100, 100))
                line += random.choice(separators) + char + random.choice(separators)
            line = line.strip()
            f.write(line + "\n")


err_file = "err_datasets.txt"
create_err_file(err_file)


def check_lines_against_regex(read_file, write_file):
    with open(read_file, "r") as read_f:
        with open(write_file, 'w') as write_f:
            for _, line in enumerate(read_f, start=1):
                line = line.strip()
                # заменяем в строке line все вхождения символов, отличных от 0-9,
                # символа '-' для отрицательных чисел, а также разрешённого разделителя ','
                # на разделитель ','
                line = re.compile(r'[^0-9-,]').sub(",", line)
                # возможно образовались пары разделителей ',,'
                # заменим их на одно вхождение ','
                line = re.compile(r'(,,)').sub(",", line)
                # уберём ',' в начале и в конце строки
                line = re.compile(r'(^,)|(,$)').sub("", line)
                write_f.write(line + "\n")


norm_datasets = "norm_datasets.txt"
check_lines_against_regex(err_file, norm_datasets)
