import ast
import json

import sublime
import sublime_plugin
from rich import print
from rich.console import Console
from rich.table import Table


class TextBoxSharpCommand(sublime_plugin.TextCommand):
    def format_text_box(self, text, width=60, wall_size=4):
        """
        Форматирует текст в блок с рамкой и автоматическим переносом строк.

        Args:
            text (str): Текст для форматирования (может быть многострочным)
            width (int): Общая ширина блока
            wall_size (int): Размер боковых стенок (количество #)

        Returns:
            str: Отформатированный текст в рамке
        """
        try:
            # Убеждаемся, что параметры являются числами
            width = 60 if not isinstance(width, (int, str)) else int(width)
            wall_size = 4 if not isinstance(wall_size, (int, str)) else int(wall_size)

            # Проверяем минимальные значения
            width = max(20, width)  # Минимальная ширина 20
            wall_size = max(1, min(10, wall_size))  # Размер стенки от 1 до 10

            # Создаем верхнюю и нижнюю границы
            border = '#' * width

            # Вычисляем доступную ширину для текста
            content_width = width - (wall_size * 2 + 2)  # 2 для пробелов вокруг текста

            # Разбиваем входной текст на строки
            input_lines = text.strip().split('\n')

            # Функция для разбиения строки на части подходящей длины
            def wrap_line(line):
                words = line.split()
                wrapped_lines = []
                current_line = []
                current_length = 0

                for word in words:
                    # Проверяем, поместится ли слово в текущую строку
                    if current_length + len(word) + (1 if current_line else 0) <= content_width:
                        current_line.append(word)
                        current_length += len(word) + (1 if current_line else 0)
                    else:
                        # Если строка не пустая, добавляем её в результат
                        if current_line:
                            wrapped_lines.append(' '.join(current_line))
                        # Начинаем новую строку с текущим словом
                        current_line = [word]
                        current_length = len(word)

                # Добавляем последнюю строку, если она есть
                if current_line:
                    wrapped_lines.append(' '.join(current_line))

                return wrapped_lines

            # Форматируем все строки с учетом переноса
            formatted_lines = []
            wall = '#' * wall_size

            for line in input_lines:
                wrapped = wrap_line(line)
                for wrapped_line in wrapped:
                    # Центрируем текст в доступном пространстве
                    padded_line = wrapped_line.center(content_width)
                    formatted_line = f'{wall} {padded_line} {wall}'
                    formatted_lines.append(formatted_line)

            # Собираем все части вместе
            result = [border]
            result.extend(formatted_lines)
            result.append(border)

            return '\n'.join(result)

        except (ValueError, TypeError) as e:
            # В случае ошибки возвращаем оригинальный текст
            sublime.error_message(f'Error formatting text box: {str(e)}')
            return text

    def run(self, edit):
        # Получаем настройки из конфигурации (если нужно)
        settings = sublime.load_settings('TextBoxSharp.sublime-settings')
        default_width = settings.get('default_width', 60)
        default_wall_size = settings.get('default_wall_size', 4)

        for selection in self.view.sel():
            if not selection.empty():
                # Получаем выделенный текст
                text = self.view.substr(selection)
                try:
                    # Форматируем текст с значениями по умолчанию
                    formatted_text = self.format_text_box(text, width=default_width, wall_size=default_wall_size)
                    # Заменяем выделенный текст отформатированным
                    self.view.replace(edit, selection, formatted_text)
                except Exception as e:
                    sublime.error_message(f'Error: {str(e)}')


class ConvertTableToTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                # Get the selected text
                text = self.view.substr(region)

                # Remove table borders and split into lines
                lines = text.strip().split('\n')
                lines = [line.strip() for line in lines if line.strip()]
                lines = [line[1:-1] for line in lines if line.startswith('│')]

                # Extract data from each line
                result = []
                for line in lines:
                    parts = [part.strip() for part in line.split('│') if part.strip()]
                    result.append(' - '.join(parts))

                # Join the results and replace the selection
                new_text = '\n'.join(result)
                self.view.replace(edit, region, new_text)

    def is_enabled(self):
        # Enable the command only if there is a selection
        return any(not region.empty() for region in self.view.sel())


class TextRichTableCommand(sublime_plugin.TextCommand):
    def parse_input(self, input_str):
        rows = input_str.strip().split('\n')
        data = []
        max_cols = 0
        for row in rows:
            cols = [x.strip() for x in row.split(' - ')]
            data.append(cols)
            max_cols = max(max_cols, len(cols))
        return data, max_cols

    def is_enabled(self):
        # Enable the command only if there is a selection
        return any(not region.empty() for region in self.view.sel())

    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                data, num_cols = self.parse_input(text)

                # Find max width for each column
                max_widths = [0] * num_cols
                for row in data:
                    for i, cell in enumerate(row):
                        max_widths[i] = max(max_widths[i], len(cell))

                table = Table(
                    show_header=False,
                    expand=True,
                    padding=(0, 1),  # Добавляем padding (отступ) слева и справа
                    show_lines=True,
                )

                # Add columns based on the maximum number of columns
                for _ in range(num_cols):
                    table.add_column('', justify='left')  # Выравнивание по левому краю

                # Add rows to the table
                for row in data:
                    table.add_row(*row)

                # Calculate console width based on max column widths
                console_width = (
                    sum(max_widths) + (num_cols - 1) * 1 + num_cols * 2 + 2
                )  # +2 for borders, *1 for space between columns, *2 for padding

                console = Console(width=console_width, record=True)
                console.print(table)
                self.view.replace(edit, selection, console.export_text())


class TextAlignLikeTableCommand(sublime_plugin.TextCommand):
    def create_table(self, text):
        lines = text.split('\n')

        # Определяем максимальную ширину столбцов
        column_widths = []
        for line in lines:
            words = line.split()
            for i, word in enumerate(words):
                if len(column_widths) <= i:
                    column_widths.append(len(word))
                else:
                    column_widths[i] = max(column_widths[i], len(word))

        # Выравниваем текст в столбцы
        aligned_lines = []
        for line in lines:
            words = line.split()
            formatted_line = ' '.join([word.ljust(width) for word, width in zip(words, column_widths)])
            aligned_lines.append(formatted_line)

        return '\n'.join(aligned_lines)

    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                print(text.split('\n'))
                self.view.replace(edit, selection, self.create_table(text))


class TextAlignLikeTable2Command(sublime_plugin.TextCommand):
    def create_table(self, text):
        split_sentences = []
        for line in text.split('\n'):
            if ':' in line:
                head, tail = line.split(':', 1)  # Split only at the first colon
                split_sentences.append([head, tail])
            else:
                split_sentences.append([line, ''])  # Handle lines without colons

        if not split_sentences:
            return text

        max_head = max([len(x[0]) for x in split_sentences])

        return '\n'.join([f'{x[0].ljust(max_head)} : {x[1]}' for x in split_sentences])

    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                self.view.replace(edit, selection, self.create_table(text))


class TextAlignLikeTable3Command(sublime_plugin.TextCommand):
    def create_table(self, text):
        split_sentences = [x.split('.') for x in text.split('\n')]
        max_head = max([len(x[0]) for x in split_sentences])
        max_tail = max([len(x[1]) for x in split_sentences])
        return '\n'.join([f'{x[0].ljust(max_head)} . {x[1].ljust(max_tail)}' for x in split_sentences])

    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                print(text.split('\n'))
                self.view.replace(edit, selection, self.create_table(text))


class TextAlignLikeTable4Command(sublime_plugin.TextCommand):
    def create_table(self, text):
        split_sentences = [x.split('-') for x in text.split('\n')]
        max_head = max([len(x[0]) for x in split_sentences])
        max_tail = max([len(x[1]) for x in split_sentences])
        return '\n'.join([f'{x[0].ljust(max_head)} - {x[1].ljust(max_tail)}' for x in split_sentences])

    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                print(text.split('\n'))
                self.view.replace(edit, selection, self.create_table(text))


class TextAlignLikeTable5Command(sublime_plugin.TextCommand):
    def create_table(self, text):
        split_sentences = [x.split('=') for x in text.split('\n')]
        max_head = max([len(x[0]) for x in split_sentences])
        max_tail = max([len(x[1]) for x in split_sentences])
        return '\n'.join([f'{x[0].ljust(max_head)} = {x[1].ljust(max_tail)}' for x in split_sentences])

    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                print(text.split('\n'))
                self.view.replace(edit, selection, self.create_table(text))


class TextAlignTableCommand(sublime_plugin.TextCommand):
    def create_table(self, lines, delimeter='-', border_h='─', border_v=''):
        rows = [line.split(f' {delimeter} ') for line in lines if line != '']
        column_widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]

        def create_separator():
            return border_h + border_h.join(border_h * (width + 2) for width in column_widths) + border_h

        def create_data_row(row):
            return (
                border_v
                + border_v.join(f' {word.center(width + 1)}' for word, width in zip(row, column_widths))
                + border_v
            )

        table = [create_separator()]
        for row in rows:
            table.append(create_data_row(row))
            table.append(create_separator())

        return '\n'.join(table)

    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                print(text.split('\n'))
                self.view.replace(edit, selection, self.create_table(text.split('\n')))


class TextAlignListCommand(sublime_plugin.TextCommand):
    def align_text_with_numbering2(self, text):
        lines = text.split('\n')
        max_length = max(len(line.split('-')[0]) for line in lines if '-' in line)

        return '\n'.join(
            f'{i + 1:1}.) {line.split("-")[0].ljust(max_length)}-{line.split("-")[1]}' if '-' in line else line
            for i, line in enumerate(lines)
        )

    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                self.view.replace(edit, selection, self.align_text_with_numbering2(text))


class JsonPretyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                new = sublime.active_window().new_file()
                new.set_scratch(True)
                new.set_name('Formatted Data')

                text = self.view.substr(selection)

                try:
                    # Попытка декодировать как JSON
                    res = json.loads(text)
                    format_text = json.dumps(res, indent=4, ensure_ascii=False)
                    new.run_command('insert_formatted_json', {'text': format_text})
                except json.decoder.JSONDecodeError:
                    try:
                        # Попытка интерпретировать как словарь Python
                        res = ast.literal_eval(text)
                        if isinstance(res, dict):
                            format_text = json.dumps(res, indent=4, ensure_ascii=False)
                            new.run_command('insert_formatted_json', {'text': format_text})
                        else:
                            sublime.error_message('Selected text is not a valid JSON or Python dict')
                    except (ValueError, SyntaxError):
                        sublime.error_message('Selected text is not a valid JSON or Python dict')


class InsertFormattedJsonCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        self.view.insert(edit, 0, text)
