import os
import random
import re
import datetime
import logging

# logging.disable(logging.CRITICAL)

if logging.getLogger().isEnabledFor(logging.CRITICAL):
    logging.basicConfig(filename=f'log-task-1-3-{os.path.basename(__file__)}-{datetime.datetime.now()}.txt',
                        level=logging.DEBUG,
                        format=' %(asctime)s - %(levelname)s - %(message)s'
                        )


def create_err_file(filename: str, separators: list):
    """
    Создаёт файл с записями, в которых числа разделены символами из списка separators
    """
    logging.debug(f"Начало {create_err_file.__name__}()")
    with open(filename, "w") as f:
        # создадим файл на 10000 записей
        for _ in range(10000):
            # длина каждой записи - от 1 до 100 чисел
            line_length = random.randint(1, 100)
            line = ""
            for _ in range(line_length):
                # числа в диапазоне от -100 до 100
                char = str(random.randint(-100, 100))
                # каждое число может предваряться и оканчиваться каким-либо разделителем
                line += random.choice(separators) + char + random.choice(separators)
            line = line.strip()
            f.write(line + "\n")
    logging.debug(f"Конец {create_err_file.__name__}()")


def check_lines(read_file, write_file):
    """
    Проверяет и исправляет строки на валидные
    """
    logging.debug(f"Начало {check_lines.__name__}()")
    with open(read_file, "r") as read_f:
        with open(write_file, 'w') as write_f:
            for _, line in enumerate(read_f, start=1):
                line = line.strip()
                logging.debug(line)
                # заменяем в строке line все вхождения символов, отличных от 0-9,
                # символа '-' для отрицательных чисел,
                # а также разрешённого разделителя ',' (если он есть)
                # на разделитель ','
                line = re.compile(r'[^0-9-,]').sub(",", line)
                logging.debug(line)
                # возможно образовались подпоследовательности разделителей ', ...,'
                # заменим их на одно вхождение ','
                line = re.compile(r'(,+)').sub(",", line)
                logging.debug(line)
                # уберём ',' в начале и в конце строки
                line = re.compile(r'(^,)|(,$)').sub("", line)
                logging.debug(line)
                logging.debug("---")
                write_f.write(line + "\n")
    logging.debug(f"Конец {check_lines.__name__}()")


def main():
    """
        Для некоторого проекта в области машинного обучения используются датасеты,
    состоящие из последовательностей целых чисел в диапазоне от -100 до 100, разделённых символом ','.
        При подготовке датасетов были допущены ошибки, в результате которой числа разделены неверно,
    а именно:
        - числа могут быть разделены не только символом ',';
        - между числами могут идти подряд несколько разделителей;
        - числовые последовательности могут начинаться и оканчиваться разделительными символами.
        Воспользуемся регулярными выражениями, чтобы очистить датасеты.
    """
    logging.debug(f"Начало {main.__name__}()")

    err_file = "err_datasets.txt"
    separators = [",", ";", "."]
    create_err_file(err_file, separators)

    norm_datasets = "norm_datasets.txt"
    check_lines(err_file, norm_datasets)

    logging.debug(f"Конец {main.__name__}()")


if __name__ == "__main__":
    logging.debug(f"Начало работы скрипта {os.path.basename(__file__)}")
    main()
    logging.debug(f"Конец работы скрипта {os.path.basename(__file__)}")
