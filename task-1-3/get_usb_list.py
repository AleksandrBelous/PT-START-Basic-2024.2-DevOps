import paramiko
import os
import re
import datetime
import logging

# logging.disable(logging.CRITICAL)
logging.basicConfig(filename=f'task-1-3-{os.path.basename(__file__)}-log-{datetime.datetime.now()}.txt',
                    level=logging.DEBUG,
                    format=' %(asctime)s - %(levelname)s - %(message)s'
                    )

from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

host = os.getenv('HOST')
port = os.getenv('PORT')
username = os.getenv('USER')
password = os.getenv('PASSWORD')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=host, username=username, password=password, port=int(port),
               # look_for_keys=False,
               # disabled_algorithms={ 'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512'] }
               )

stdin, stdout, stderr = client.exec_command('journalctl -t kernel | grep usb')
data = stdout.read() + stderr.read()
client.close()
data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
print(data)


def main():
    """
    """
    logging.debug(f"Начало {main.__name__}()")

    logging.debug(f"Конец {main.__name__}()")


if __name__ == "__main__":
    logging.debug(f"Начало работы скрипта {os.path.basename(__file__)}")
    main()
    logging.debug(f"Конец работы скрипта {os.path.basename(__file__)}")
