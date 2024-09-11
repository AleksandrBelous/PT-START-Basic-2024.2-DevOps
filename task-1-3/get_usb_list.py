import paramiko
import os

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

stdin, stdout, stderr = client.exec_command('free -h')
data = stdout.read() + stderr.read()
client.close()
data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
print(data)
