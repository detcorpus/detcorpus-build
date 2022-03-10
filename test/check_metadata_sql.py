import argparse
import re
"""
Скрипт для вывода индексов строк в файле metadata.sql, 
которые содержат переносы строк внутри VALUES ().
"""

# наход
# ит ошибки лишнего переноса строк в файле sql
def find_errors(file_path):
    with open(file_path, 'r') as f:
        # список для будущих номеров строк с ошибками
        found_errors = []
        # флаг начала парсинга
        start_parse = False
        # регулярное выражение для строки
        reg_exp = r'INSERT INTO ([a-zA-Z"_]+) VALUES \((.+?)\);\n'
        for ind, line in enumerate(f):
            # найдем место первого INSERT
            if not start_parse:
                if not line.strip().startswith('INSERT'):
                    continue
                start_parse = True
            elif line.startswith('COMMIT'):
                break
            # строка с INSERT должна полностью соответствовать регулярному выражению
            m = re.match(reg_exp, line)
            # проверяем, есть ли ошибка в строке
            if not m:
                found_errors.append(ind+1)
                continue
            if m.end() != len(line):
                found_errors.append(ind+1)

    return found_errors


def main(args):
    errors_ind = find_errors(args.input_file)
    if errors_ind:
        print('Номера строк с ошибками:')
        print(errors_ind)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # путь к файлу metadata.sql
    parser.add_argument("-i", "--input-file", required=True)
    args = parser.parse_args()
    main(args)
