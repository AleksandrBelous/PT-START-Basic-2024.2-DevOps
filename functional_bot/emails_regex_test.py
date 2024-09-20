import re

text = ("kolbeev@example.compoiuytrewq,./;[]=-0987654321~!@#$%^&*()"
        "artem.world@sevsu.ru|}{:?><,./;[]=-0987654321!@#$%^&*()"
        "support@site.compoiuytrewq,./;[]=-0987654321~!@#$%^&*()"
        "admin@example.ru|}{:?><,./;[]=-0987654321!@#$%^&()"
        "user123@gmail.compoiuytrewq,./;[]=-0987654321~!@#$%^&*()"
        "test@yandex.ru.|}{:?><,./;[]=-0987654321~!@#$%^&()_")

emailsRegex = re.compile(r'[a-zA-Z0-9.]+@[a-zA-Z0-9.]+\.[a-zA-Z]{2,3}')

emailsList = emailsRegex.findall(text)
print(*emailsList, sep='\n')
