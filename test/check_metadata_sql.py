import argparse
import re
"""
Скрипт для вывода индексов строк в файле metadata.sql, 
которые 
-содержат переносы строк внутри VALUES ().
-содержат ascii символы
-являются повторяющими строками для таблицы text_author
"""


# находит ошибки в файле metadata.sql
def find_errors(file_path, fix=True):
    # если надо исправлять текст, создаем пустую переменную под исправленный текст
    if fix is True:
        new_text = ''
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
                    # добавляем строку без изменений в исправленный текст, если это необходимо
                    if fix is True:
                        new_text += line
                    continue
                start_parse = True
            elif line.startswith('COMMIT'):
                # добавляем строку без изменений в исправленный текст, если это необходимо
                if fix is True:
                    new_text += line
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
            # для строки с найденными недопустимыми кавычками в значениях
            if values.find('"') >= 0:
                errors_string['ascii'].append(ind)
                # если надо исправлять текст
                if fix is True:
                    # словарь для сопоставления предыдущей кавычки и подходящей к ней закрывающей (на замену текущей)
                    quotes_dict = {'«': '»', '„': '“', '“': '”'}
                    # все допустимые кавычки в значениях
                    quotes_set = {'«', '»', '„', '“', '“'}
                    # список текущих кавычек в строке
                    quotes = []
                    # создаем новую строку, записываем туда текст до самих значений
                    new_string = f'INSERT INTO {m.group(1)} VALUES ('
                    # проходимся посимвольно по строке
                    for s in values:
                        # если нашли недопустимую кавычку
                        if s == '"':
                            # если сейчас все кавычки закрыты (в строке их парное кол-во)
                            if len(quotes) % 2 == 0:
                                # то заменяем " на «
                                quotes.append('«')
                                new_string += '«'
                            # если последние кавычки не закрыты, находим правильную закрывающую кавычку
                            # на которую меняем "
                            else:
                                new_qoute = quotes_dict[quotes[-1]]
                                new_string += new_qoute
                                quotes.append(new_qoute)
                        # если нашли допустимую кавычку, записываем ее
                        elif s in quotes_set:
                            quotes.append(s)
                            new_string += s
                        # если иной символ - просто присоединяем к новой строке
                        else:
                            new_string += s

                    # дописываем в конец новой строки оставшиеся нужные символы
                    new_string += ');\n'
                    # добавляем новую строку в исправленный текст
                    new_text += new_string

            # для строки без недопустимых кавычек, записываем ее в исправленный текст, если это необходимо
            else:
                if fix is True:
                    new_text += line

    if fix is True:
        return new_text, errors_string
    return errors_string


def main(args):
    if args.fix:
        new_data, errors = find_errors(args.input_file, fix=True)
        with open(args.input_file, 'w') as f:
            f.write(new_data)
    else:
        errors = find_errors(args.input_file, fix=False)
    # ощибки с переносом строк
    print(f"несоответствие шаблону строки (возможная проблема лишних переносов): {errors['bad_strings']}")
    # повторяющиеся строки в таблице text_author
    print(f"повторяющиеся строки в таблице text_author (повторяющаяся строка, первое вхождение): {errors['text_author']}")
    # ascii символы
    print(f"ascii-кавычки (исправлено): {errors['ascii']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # путь к файлу metadata.sql
    parser.add_argument("-i", "--input-file", required=True)
    parser.add_argument("-f", "--fix", required=False, default=True)
    args = parser.parse_args()
    main(args)
