import random


def create_rubbished_file(filename: str):
    with open(filename, "w") as f:
        for _ in range(10000):
            line_length = random.randint(1, 100)
            line = ""
            for _ in range(line_length):
                char = str(random.randint(-100, 100))
                line += char + random.choice([",", ";", "."])
            line = line.strip()
            f.write(line + "\n")


rubbished_file = "err_datasets.txt"
create_rubbished_file(rubbished_file)
