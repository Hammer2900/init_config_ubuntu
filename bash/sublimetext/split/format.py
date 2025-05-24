import ast
import json
import re

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


class TextAlignHierarchicalWorkerCommand(sublime_plugin.TextCommand):
    def run(self, edit, original_selections_regions_tuples, user_separators_str):
        print('[Worker] Run called')
        print(f'[Worker] Original selections: {original_selections_regions_tuples}')
        print(f"[Worker] User separators string: '{user_separators_str}'")

        user_separators = [s.strip() for s in user_separators_str.split(' ') if s.strip()]
        # It's important that user_separators itself is what's passed,
        # as _align_text_hierarchically will now interpret it.
        print(f'[Worker] Parsed separators to be passed: {user_separators}')

        if not user_separators:
            sublime.status_message('No valid separators provided to worker.')
            print('[Worker] No valid separators, exiting.')
            return

        replaced_something = False
        for i, sel_region_tuple in enumerate(reversed(original_selections_regions_tuples)):
            print(
                f'[Worker] Processing selection {i+1}/{len(original_selections_regions_tuples)}: Region {sel_region_tuple}'
            )
            sel_region = sublime.Region(sel_region_tuple[0], sel_region_tuple[1])
            if sel_region.empty():
                print(f'[Worker] Selection {i+1} is empty, skipping.')
                continue

            original_text = self.view.substr(sel_region)
            # print(f"[Worker] Selection {i+1} original text:\n'''{original_text}'''")

            processed_text = self._align_text_hierarchically(
                original_text,
                user_separators,  # Pass the parsed list
            )
            # print(f"[Worker] Selection {i+1} processed text:\n'''{processed_text}'''")

            if original_text == processed_text:
                print(f'[Worker] Selection {i+1} - original and processed text are identical. No replacement.')
            else:
                print(f'[Worker] Selection {i+1} - REPLACING TEXT.')
                self.view.replace(edit, sel_region, processed_text)
                replaced_something = True

        if original_selections_regions_tuples:
            # Use the initially parsed user_separators for the status message,
            # as this reflects what the user intended at a high level.
            display_separators = [s.strip() for s in user_separators_str.split(' ') if s.strip()]
            if not display_separators:  # Should not happen if we reached here, but good practice
                display_separators = ['<none>']

            if replaced_something:
                sublime.status_message(f"Aligned with: {', '.join(display_separators)}")
                print('[Worker] Status message: Aligned.')
            else:
                sublime.status_message(f"No changes made with: {', '.join(display_separators)}")
                print('[Worker] Status message: No changes made.')

    def _align_text_hierarchically(self, text, original_separators_input):
        print(f'[_align_text_hierarchically] Called. Original separators input: {original_separators_input}')

        input_lines_raw = text.splitlines()
        if not input_lines_raw:
            print('[_align_text_hierarchically] No input lines, returning original text.')
            return text

        # --- New logic to determine mode ---
        is_single_separator_mode = False
        single_separator_for_splitting = None
        separators_for_hierarchical_processing = []

        if not original_separators_input:  # Should have been caught by caller
            print('WARN: _align_text_hierarchically called with no separators.')
            return text

        # Check if all separators in the input list are identical
        first_sep_in_input = original_separators_input[0]
        if all(s == first_sep_in_input for s in original_separators_input):
            is_single_separator_mode = True
            single_separator_for_splitting = first_sep_in_input
            # For logging consistency, though not used directly by single mode for splitting parts
            separators_for_hierarchical_processing = [single_separator_for_splitting]
            print(
                f"[_align_text_hierarchically] All input separators are identical ('{single_separator_for_splitting}'). Engaging SINGLE separator mode."
            )
        else:
            is_single_separator_mode = False
            separators_for_hierarchical_processing = original_separators_input
            # single_separator_for_splitting remains None
            print(
                f'[_align_text_hierarchically] Input separators are distinct. Engaging HIERARCHICAL mode with: {separators_for_hierarchical_processing}'
            )
        # --- End of new logic to determine mode ---

        all_lines_data = []
        max_parsed_cols = 0

        for line_idx, line_content in enumerate(input_lines_raw):
            if not line_content.strip():
                all_lines_data.append({'parts': [''], 'seps': [], 'is_empty': True})
                continue

            current_line_parts = []
            used_separators_for_this_line = []

            if is_single_separator_mode:
                # SINGLE SEPARATOR MODE: split by all occurrences of single_separator_for_splitting
                parts_from_split = line_content.split(single_separator_for_splitting)
                current_line_parts = [p.strip() for p in parts_from_split]
                if len(parts_from_split) > 1:
                    used_separators_for_this_line = [single_separator_for_splitting] * (len(parts_from_split) - 1)
                # print(
                #     f"[_align_text_hierarchically] Line {line_idx} (single_sep_mode) parts: {current_line_parts}, seps: {used_separators_for_this_line}"
                # )

            else:
                # HIERARCHICAL MODE: use partition with separators_for_hierarchical_processing
                remaining_text_in_line = line_content
                for sep_to_find in separators_for_hierarchical_processing:  # Use the determined list
                    head, found_separator, tail = remaining_text_in_line.partition(sep_to_find)
                    if found_separator:
                        current_line_parts.append(head.strip())
                        used_separators_for_this_line.append(found_separator)
                        remaining_text_in_line = tail
                    else:
                        # This hierarchical separator not found, stop trying for this line
                        break
                current_line_parts.append(remaining_text_in_line.strip())
                # print(
                #     f"[_align_text_hierarchically] Line {line_idx} (multi_sep_mode) parts: {current_line_parts}, seps: {used_separators_for_this_line}"
                # )

            all_lines_data.append(
                {
                    'parts': current_line_parts,
                    'seps': used_separators_for_this_line,
                    'is_empty': False,
                }
            )
            max_parsed_cols = max(max_parsed_cols, len(current_line_parts))

        print(f'[_align_text_hierarchically] Max parsed columns: {max_parsed_cols}')

        if max_parsed_cols == 0:
            print('[_align_text_hierarchically] Max parsed columns is 0 (no parts found), returning original text.')
            return text

        if max_parsed_cols == 1 and not any(
            line_data['seps'] for line_data in all_lines_data if not line_data['is_empty']
        ):
            print(
                '[_align_text_hierarchically] Max parsed columns is 1 AND no separators were used, returning original text.'
            )
            return text

        column_widths = [0] * max_parsed_cols
        for line_data in all_lines_data:
            if line_data['is_empty']:
                continue
            for i, part_content in enumerate(line_data['parts']):
                if i < max_parsed_cols:  # Ensure we don't go out of bounds
                    column_widths[i] = max(column_widths[i], len(part_content))
        print(f'[_align_text_hierarchically] Column widths: {column_widths}')

        output_formatted_lines = []
        for line_data in all_lines_data:
            if line_data['is_empty']:
                output_formatted_lines.append('')
                continue

            current_result_segments = []
            parts_for_this_line = line_data['parts']
            separators_for_this_line = line_data['seps']

            for i, part_content in enumerate(parts_for_this_line):
                if i < len(parts_for_this_line) - 1:  # Not the last part
                    aligned_part = part_content.ljust(column_widths[i])
                    current_result_segments.append(aligned_part)
                else:  # Last part, no padding
                    current_result_segments.append(part_content)

                if i < len(separators_for_this_line):  # If there's a separator after this part
                    current_result_segments.append(f' {separators_for_this_line[i]} ')

            final_line_str = ''.join(current_result_segments).rstrip()
            output_formatted_lines.append(final_line_str)

        result_text = '\n'.join(output_formatted_lines)
        return result_text


class TextAlignHierarchicalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('[MainCommand] Run called')
        self.original_selections_regions_tuples = [(s.begin(), s.end()) for s in self.view.sel() if not s.empty()]
        print(f'[MainCommand] Original non-empty selections: {self.original_selections_regions_tuples}')

        if not self.original_selections_regions_tuples:
            sublime.status_message('No non-empty text selected for hierarchical alignment.')
            print('[MainCommand] No non-empty selections, exiting.')
            return

        self.view.window().show_input_panel(
            'Enter separators (comma-separated for hierarchy, or single for all occurrences):',  # Обновил подсказку
            ':',
            self.on_done_input,
            None,
            self.on_cancel_input,
        )
        print('[MainCommand] Input panel shown.')

    def on_done_input(self, user_input_string):
        print(f"[MainCommand] on_done_input called with: '{user_input_string}'")
        separators_str = user_input_string.strip()
        if not separators_str:
            sublime.status_message('No separators entered.')
            print('[MainCommand] No separators entered by user, exiting.')
            return

        if not hasattr(self, 'original_selections_regions_tuples') or not self.original_selections_regions_tuples:
            print('[MainCommand] Error: original_selections_regions_tuples not found or empty in on_done_input.')
            sublime.status_message('Error: Selection data lost.')
            return

        print(
            f"[MainCommand] Running worker command with selections: {self.original_selections_regions_tuples} and separators_str: '{separators_str}'"
        )
        self.view.run_command(
            'text_align_hierarchical_worker',
            {  # Убрано подчеркивание
                'original_selections_regions_tuples': self.original_selections_regions_tuples,
                'user_separators_str': separators_str,
            },
        )

    def on_cancel_input(self):
        print('[MainCommand] on_cancel_input called.')
        sublime.status_message('Hierarchical alignment cancelled.')

    def is_enabled(self):
        return any(not sel.empty() for sel in self.view.sel())


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


class TextAlignBySeparatorCommand(sublime_plugin.TextCommand):
    def create_aligned_table(self, text, separator):
        lines = text.split('\n')
        if not lines:
            return text

        # 1. Разделить каждую строку на части по указанному separator и убрать лишние пробелы
        split_lines_content = []
        for line_idx, line in enumerate(lines):
            # Если строка пустая, сохраняем ее как есть, чтобы не ломать пустые строки в выделении
            if not line.strip():
                split_lines_content.append(None)  # Используем None как маркер пустой строки
                continue
            parts = [part.strip() for part in line.split(separator)]
            split_lines_content.append(parts)

        if not any(slc is not None for slc in split_lines_content):  # Если все строки были пустыми или не было строк
            return text

        # 2. Определить максимальное количество столбцов (игнорируя None для пустых строк)
        max_cols = 0
        for parts in split_lines_content:
            if parts is not None:
                max_cols = max(max_cols, len(parts))

        if max_cols == 0:  # Если все строки были пустыми или не содержали частей
            return '\n'.join(
                l if l is not None else '' for l in lines
            )  # Возвращаем исходные строки (пустые остаются пустыми)

        # 3. Рассчитать максимальную ширину для каждого столбца
        column_widths = [0] * max_cols
        for parts in split_lines_content:
            if parts is None:
                continue
            for i, part_content in enumerate(parts):
                if i < max_cols:
                    column_widths[i] = max(column_widths[i], len(part_content))

        # 4. Сформировать отформатированные строки
        output_lines = []
        join_separator = f' {separator} '  # Разделитель, который будет вставлен между столбцами

        for parts in split_lines_content:
            if parts is None:  # Если это была пустая строка
                output_lines.append('')
                continue

            formatted_parts = []
            for i, part_content in enumerate(parts):
                if i < max_cols:
                    # Последний столбец в строке не требует ljust, если он действительно последний
                    # Но для единообразия и если после него может быть что-то (хотя тут не будет), оставим ljust
                    # Однако, если это последний столбец И он последний в данной строке, ljust не нужен.
                    # Но для простоты и предсказуемости, выравниваем все столбцы, кроме последнего в строке, если он не единственный.
                    if i < len(parts) - 1:  # Если это не последняя часть текущей строки
                        formatted_parts.append(part_content.ljust(column_widths[i]))
                    else:  # Последняя часть текущей строки
                        formatted_parts.append(part_content)  # Не добавляем лишних пробелов справа

            output_lines.append(join_separator.join(formatted_parts))

        return '\n'.join(output_lines)

    def run(self, edit, separator=':'):  # separator по умолчанию ":"
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                # Передаем separator в create_aligned_table
                self.view.replace(edit, selection, self.create_aligned_table(text, separator))


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


class SortLinesByFirstCharacterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                # Get the selected text
                text = self.view.substr(region)

                # Split the text into lines
                lines = text.splitlines()

                # Sort the lines based on the first character (alphanumeric or symbol)

                def sort_key(line):
                    match = re.match(r'^\W*([\w\d])', line)
                    if match:
                        return match.group(1).lower()
                    else:
                        return ''

                sorted_lines = sorted(lines, key=sort_key)

                # Join the sorted lines back into a single string
                sorted_text = '\n'.join(sorted_lines)

                # Replace the selected text with the sorted text
                self.view.replace(edit, region, sorted_text)
