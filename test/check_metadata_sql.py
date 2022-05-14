import argparse
import re
import csv
"""
Скрипт для вывода индексов строк в файле metadata.sql, 
которые 
-содержат переносы строк внутри VALUES ().
-содержат ascii символы
-являются повторяющими строками для таблицы text_author
"""


# находит ошибки в файле metadata.sql

def find_errors(file_path):
    with open(file_path, 'r') as f:
        # для будущих строк с ошибками
        errors_string = {'text_author': [], 'bad_strings': [], 'ascii': []}
        # множество всех строк для таблицы text_author
        text_author_strings = dict()
        # флаг начала парсинга
        start_parse = False
        # регулярное выражение для строки
        reg_exp = r'INSERT INTO ([a-zA-Z"_]+) VALUES \((.+?)\);\n'

        for i, line in enumerate(f):

            ind = i + 1
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
            # когда строка не соотвествует шаблону (проверка на переносы строк)
            if not m or m.end() != len(line):
                errors_string['bad_strings'].append(ind)
                continue

            # проверяем на повторяющиеся значения в таблице text_author
            text_author_flag = 'INSERT INTO "text_author" VALUES '
            is_text_author = line.find(text_author_flag) == 0
            if is_text_author:
                value = line[len(text_author_flag):]
                if value in text_author_strings:
                    errors_string['text_author'].append((ind, text_author_strings[value]))
                else:
                    text_author_strings[value] = ind

            # проверяем, имеются ли в тексте ascii-кавычки
            values = m.group(2)
            if values.find('"') >= 0:
                errors_string['ascii'].append(ind)

    return errors_string


def main(args):
    errors = find_errors(args.input_file)
    # ощибки с переносом строк
    print(f"несоответствие шаблону строки (возможная проблема лишних переносов): {errors['bad_strings']}")
    # повторяющиеся строки в таблице text_author
    print(f"повторяющиеся строки в таблице text_author (повторяющаяся строка, первое вхождение): {errors['text_author']}")
    # ascii символы
    print(f"ascii-кавычки: {errors['ascii']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # путь к файлу metadata.sql
    parser.add_argument("-i", "--input-file", required=True)
    args = parser.parse_args()
    main(args)
