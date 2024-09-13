import paramiko
import os
import re
import datetime
import calendar
import logging

# logging.disable(logging.CRITICAL)

if logging.getLogger().isEnabledFor(logging.CRITICAL):
    logging.basicConfig(filename=f'task-1-3-{os.path.basename(__file__)}-log-{datetime.datetime.now()}.txt',
                        level=logging.DEBUG,
                        format=' %(asctime)s - %(levelname)s - %(message)s'
                        )

from dotenv import load_dotenv
from pathlib import Path


def create_journalctl_file(filename: str, command: str):
    logging.debug(f"Начало {create_journalctl_file.__name__}()")

    dotenv_path = Path('.env')
    load_dotenv(dotenv_path=dotenv_path)

    host = os.getenv('HOST')
    port = os.getenv('PORT')
    username = os.getenv('USER')
    password = os.getenv('PASSWORD')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=int(port))

    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    # print(data)
    with open(filename, "w") as f:
        f.write(data)

    logging.debug(f"Конец {create_journalctl_file.__name__}()")


def get_days_in_month(month_name):
    month_days = {
            "Jan": 31,
            "Feb": None,
            "Mar": 31,
            "Apr": 30,
            "May": 31,
            "Jun": 30,
            "Jul": 31,
            "Aug": 31,
            "Sep": 30,
            "Oct": 31,
            "Nov": 30,
            "Dec": 31
            }

    year = datetime.datetime.now().year

    month_days["Feb"] = 29 if calendar.isleap(year) else 28

    return month_days[month_name]


def check_usb_devs(read_file, write_file):
    logging.debug(f"Начало {check_usb_devs.__name__}()")

    dt = datetime.datetime.now()
    month, day = dt.strftime("%b"), dt.day

    main_info = set()

    with open(read_file, "r") as read_f:
        with open(write_file, 'w') as write_f:
            for _, line in enumerate(read_f, start=1):
                line = line.strip()
                try:
                    # найдём строки, которые содержат дату текущего месяца,
                    # а также текущий день, 1 день назад и 2 дня назад;
                    # сделаем обрезание дня по модулю числа дней в месяце;
                    # в последней пустой группе сохраним строку без указания даты
                    mod = get_days_in_month(month)

                    template = re.compile(fr'^({month})\s(({day})|({(day - 1) % mod})|({(day - 2) % mod}))\s([0-9]{2}:){2}[0-9].*\s(.*)')
                    line = template.search(line)
                    print(line.groups())
                    month_, day_, line = line.groups()[0], line.groups()[1], line.groups()[-1]

                    # найдём строки, которые содержат idVendor и idProduct
                    template = re.compile(r'.*(idVendor)=([0-9a-z]{4}),\s(idProduct)=([0-9a-z]{4})')
                    _, idVendor_, _, idProduct_ = template.search(line).groups()
                    tpl = (month_, day_, idVendor_, idProduct_)
                    logging.debug(tpl)

                    if tpl not in main_info:
                        main_info.add(tpl)
                except AttributeError:
                    continue

            if main_info:
                for tpl in sorted(main_info, key=lambda tpl: tpl[1]):
                    write_f.write(f"{tpl[0]} {tpl[1]}, {tpl[2]}:{tpl[3]}\n")

    logging.debug(f"Конец {check_usb_devs.__name__}()")


def main():
    """
    """
    logging.debug(f"Начало {main.__name__}()")
    journal = "journalctl.txt"

    create_journalctl_file(journal, "journalctl -t kernel | grep usb")

    usd_devs = "usb_devs.txt"
    check_usb_devs(journal, usd_devs)

    logging.debug(f"Конец {main.__name__}()")


if __name__ == "__main__":
    logging.debug(f"Начало работы скрипта {os.path.basename(__file__)}")
    main()
    logging.debug(f"Конец работы скрипта {os.path.basename(__file__)}")
