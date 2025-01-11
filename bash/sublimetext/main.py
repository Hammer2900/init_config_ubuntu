import sublime
import sublime_plugin
import os
import re
import urllib.request
import subprocess
import contextlib
import json
import pprint
import threading
import shlex
import asyncio
import signal
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich import print, pretty, inspect
from slugify import slugify
from art import text2art
import pretty_errors
import queue
import http.client
from datetime import datetime, timezone, timedelta
import ast


class RenumberLinesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                lines = text.split('\n')
                new_lines = []
                counter = 1
                first_line_processed = False

                for line in lines:
                    if not first_line_processed:
                        if any(c.isdigit() for c in line) and '.' in line:
                            new_lines.append(f"{counter}. {line[line.find('.') + 2:]}")
                            counter += 1
                            first_line_processed = True
                        else:
                            new_lines.append(line)
                    else:
                        if any(c.isdigit() for c in line) and '.' in line:
                            new_lines.append(f"{counter}. {line[line.find('.') + 2:]}")
                            counter += 1
                        else:
                            new_lines.append(line)

                self.view.replace(edit, region, '\n'.join(new_lines))


class SelectWordToSpacesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if region.empty():
                # Определяем границы выделения
                start = region.begin()
                end = region.end()

                # Расширяем влево до пробела
                while start > 0 and not self.view.substr(start - 1).isspace():
                    start -= 1

                # Расширяем вправо до пробела
                while end < self.view.size() and not self.view.substr(end).isspace():
                    end += 1

                # Устанавливаем новое выделение
                self.view.sel().add(sublime.Region(start, end))


class RemoveEmptyLinesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Получаем все выделенные области
        for region in self.view.sel():
            # Если область не пустая
            if not region.empty():
                # Получаем выделенный текст
                text = self.view.substr(region)
                # Разделяем текст на строки
                lines = text.splitlines()
                # Фильтруем пустые строки
                filtered_lines = [line for line in lines if line.strip()]
                # Соединяем строки обратно в текст
                new_text = '\n'.join(filtered_lines)
                # Заменяем выделенный текст на новый
                self.view.replace(edit, region, new_text)


class KyivDateTimeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Create Kyiv timezone
        kiev_timezone = timezone(timedelta(hours=3))
        current_time_kiev = datetime.now(kiev_timezone)

        # Prepare different date formats
        date_formats = [
            current_time_kiev.strftime('%Y-%m-%d %H:%M:%S'),  # Full datetime
            current_time_kiev.strftime('%Y-%m-%d'),  # Date
            current_time_kiev.strftime('%d %b %Y'),  # Day Month Year
            current_time_kiev.strftime('%A, %B %d, %Y'),  # Weekday, Month Day, Year
            current_time_kiev.strftime('%x'),  # Locale's date representation
        ]

        # Join formats with newlines
        formatted_dates = '\n'.join(date_formats)

        # Insert at each cursor position
        for region in self.view.sel():
            self.view.replace(edit, region, formatted_dates)


# class OpenSakuraTerminalCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#         window = self.view.window()
#         folders = window.folders()

#         if not folders:
#             sublime.status_message("Ошибка: Открытые папки не найдены.")
#             return

#         # Показываем пользователю список папок
#         if len(folders) > 1:
#             window.show_quick_panel(
#                 folders,
#                 lambda index: self.open_terminal(index, folders),
#                 sublime.KEEP_OPEN_ON_FOCUS_LOST,
#                 0,
#                 lambda _: None,
#             )
#         else:
#             # Если только одна папка, открываем её сразу
#             self.open_terminal(0, folders)

#     def open_terminal(self, index, folders):
#         if index == -1:  # Пользователь отменил выбор
#             sublime.status_message("Операция отменена.")
#             return

#         selected_folder = folders[index]
#         sublime.status_message(f"Открываем терминал в папке: {selected_folder}")

#         command = ["sakura", "-e", "lazygit"]

#         try:
#             subprocess.Popen(
#                 command,
#                 cwd=selected_folder,
#                 stdout=subprocess.DEVNULL,
#                 stderr=subprocess.DEVNULL,
#             )
#         except Exception as e:
#             sublime.error_message(f"Ошибка запуска приложения: {e}")


class OpenSakuraTerminalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = self.view.window()

        folders = window.folders()
        if not folders:
            sublime.status_message('Ошибка: Открытая папка не найдена.')
            return

        current_folder = folders[0]
        sublime.status_message(f'Открываем терминал в папке: {current_folder}')

        command = ['sakura', '-e', 'lazygit']

        try:
            subprocess.Popen(
                command,
                cwd=current_folder,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            sublime.error_message(f'Ошибка запуска приложения: {e}')


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


class ConsoleAutocompleteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Получаем текущую строку
        region = self.view.line(self.view.sel()[0])
        line = self.view.substr(region)

        # Получаем позицию курсора в строке
        cursor_position = self.view.sel()[0].b - region.begin()

        # Получаем предложения автодополнения
        suggestions = self.get_autocomplete_suggestions(line, cursor_position)

        # Отображаем меню с предложениями
        if suggestions:
            self.view.show_popup_menu(suggestions, lambda idx: self.on_done(idx, line, cursor_position))

    def get_autocomplete_suggestions(self, line, cursor_position):
        # Разбиваем строку на токены
        tokens = shlex.split(line[:cursor_position])

        if len(tokens) == 0 or (len(tokens) == 1 and not line.endswith(' ')):
            # Автодополнение команд
            return self.get_command_suggestions(tokens[-1] if tokens else '')
        else:
            # Автодополнение параметров и флагов
            return self.get_parameter_suggestions(tokens)

    def get_command_suggestions(self, prefix):
        try:
            output = subprocess.check_output(f'compgen -c {prefix}', shell=True, text=True)
            return output.strip().split('\n')
        except subprocess.CalledProcessError:
            return []

    def get_parameter_suggestions(self, tokens):
        command = tokens[0]
        try:
            # Получаем помощь по команде
            help_output = subprocess.check_output(f'{command} --help', shell=True, text=True, stderr=subprocess.STDOUT)

            # Извлекаем возможные параметры и флаги
            suggestions = []
            for line in help_output.split('\n'):
                if line.strip().startswith('-'):
                    suggestions.append(line.strip().split()[0])

            return suggestions
        except subprocess.CalledProcessError:
            return []

    def on_done(self, index, line, cursor_position):
        if index == -1:
            return
        selected = self.get_autocomplete_suggestions(line, cursor_position)[index]

        # Вычисляем, какую часть строки нужно заменить
        tokens = shlex.split(line[:cursor_position])
        if len(tokens) == 0 or (len(tokens) == 1 and not line.endswith(' ')):
            # Заменяем последнее слово или вставляем новую команду
            replace_region = sublime.Region(
                self.view.line(self.view.sel()[0]).begin() + line[:cursor_position].rfind(tokens[-1] if tokens else ''),
                self.view.sel()[0].b,
            )
        else:
            # Вставляем новый параметр или флаг
            replace_region = sublime.Region(self.view.sel()[0].b, self.view.sel()[0].b)

        # Используем новую команду для вставки текста
        self.view.run_command(
            'console_autocomplete_insert',
            {'text': selected, 'region': (replace_region.a, replace_region.b)},
        )


class ConsoleAutocompleteInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, text, region):
        # Заменяем выбранный регион на автодополненную версию
        self.view.replace(edit, sublime.Region(*region), text + ' ')

        # Перемещаем курсор в конец вставленного текста
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(region[0] + len(text) + 1))


class ConsoleAutocompleteListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key == 'console_autocomplete':
            return True
        return None


class HighlightToEmptyLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        current_position = view.sel()[0].begin()
        start_position = current_position

        while True:
            line_region = view.line(current_position)
            if view.substr(line_region).strip() == '':
                break
            current_position = line_region.begin() - 1
            if current_position < 0:
                break

        end_position = view.line(current_position).end()
        view.sel().clear()
        view.sel().add(sublime.Region(start_position, end_position + 1))


class HighlightToEmptyLine2Command(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        # Получаем начальную позицию курсора
        current_position = view.sel()[0].begin()

        # Поиск верхней границы
        top_position = current_position
        while True:
            line_region = view.line(top_position)
            if view.substr(line_region).strip() == '':
                break
            top_position = line_region.begin() - 1
            if top_position < 0:
                top_position = 0
                break

        # Поиск нижней границы
        bottom_position = current_position
        while True:
            line_region = view.line(bottom_position)
            if view.substr(line_region).strip() == '':
                break
            next_line = line_region.end() + 1
            if next_line >= view.size():
                bottom_position = view.size()
                break
            bottom_position = next_line

        # Получаем регионы для верхней и нижней границ
        top_line_region = view.line(top_position)
        bottom_line_region = view.line(bottom_position)

        # Создаем регион выделения от конца верхней пустой строки
        # до конца нижней пустой строки
        selection_region = sublime.Region(top_line_region.end() + 1, bottom_line_region.end())

        # Устанавливаем курсор в центр выделенного текста
        middle_point = (selection_region.begin() + selection_region.end()) // 2

        # Очищаем текущее выделение и добавляем новое
        view.sel().clear()
        view.sel().add(selection_region)

        # Прокручиваем вид, чтобы курсор был виден
        view.show(middle_point)


class AsyncRunOllamaRequestCommand(sublime_plugin.TextCommand):
    running = False
    process = None
    output_queue = None
    stop_event = None
    run_thread = None
    update_thread = None

    def run_code_async(self, code):
        try:
            conn = http.client.HTTPConnection('localhost', 11434)
            payload = json.dumps(
                {
                    # "model": "llama3.1:8b",
                    # "model": "mistral:latest",
                    # "model": "codeqwen:latest",
                    # "model": "qwen2.5:14b",
                    'model': 'trans_eng:latest',
                    # "prompt": f"[INST]{code}[/INST] you will respond with markdown only !",
                    # "prompt": f"[INST]{code}[/INST] you will respond with json only !",
                    # "prompt": f"[INST]{code}[/INST] you will respond with 100 chars in response only !",
                    'prompt': f'[INST]{code}[/INST]',
                    'stream': False,
                    'raw': False,
                    'options': {'seed': 123112, 'temperature': 0},
                }
            )
            headers = {'Content-Type': 'application/json'}
            conn.request('POST', '/api/generate', payload, headers)
            res = conn.getresponse()
            data = res.read()
            self.view.run_command(
                'insert_snippet',
                {'contents': '\n' + json.loads(data.decode('utf-8')).get('response', '-----')},
            )
        except Exception as e:
            self.view.run_command('insert_snippet', {'contents': f'Error running code: {str(e)}'})
        finally:
            AsyncRunCommand.running = False
            self.view.run_command(
                'insert_snippet',
                {
                    'contents': '\n\n# ====================================== end ====================================== #\n'
                },
            )

    def run(self, edit):
        if self.view.sel()[0].empty():
            line_region = self.view.line(self.view.sel()[0])
            code = self.view.substr(line_region)
            self.view.run_command('insert_snippet', {'contents': '\n'})
        else:
            code = self.view.substr(self.view.sel()[0])
            self.view.run_command('insert_snippet', {'contents': f'{code}\n'})

        AsyncRunCommand.run_thread = threading.Thread(target=self.run_code_async, args=(code,))
        AsyncRunCommand.run_thread.start()


class AsyncRunCommand(sublime_plugin.TextCommand):
    running = False
    process = None
    output_queue = None
    stop_event = None
    run_thread = None
    update_thread = None
    working_directory = '/dev/shm/'

    def set_working_directory(self):
        directory = self.view.substr(self.view.line(self.view.sel()[0]))
        if not os.path.isdir(directory):
            sublime.error_message(f"The directory '{directory}' does not exist.")
            return

        AsyncRunCommand.working_directory = directory

        sublime.status_message(f'Working directory set to: {directory}')

    def run(self, edit, action='run'):
        print(f'AsyncRunCommand action: {action}')
        if action == 'run':
            if AsyncRunCommand.running:
                sublime.error_message('A command is already running. Stop it first.')
                return

            AsyncRunCommand.running = True
            AsyncRunCommand.stop_event = threading.Event()
            AsyncRunCommand.output_queue = queue.Queue()

            if self.view.sel()[0].empty():
                line_region = self.view.line(self.view.sel()[0])
                code = self.view.substr(line_region)
                self.view.run_command('insert_snippet', {'contents': '\n\n'})
            else:
                code = self.view.substr(self.view.sel()[0])
                self.view.run_command('insert_snippet', {'contents': f'{code}\n'})

            AsyncRunCommand.run_thread = threading.Thread(target=self.run_code_async, args=(code,))
            AsyncRunCommand.run_thread.start()

            AsyncRunCommand.update_thread = threading.Thread(target=self.update_output)
            AsyncRunCommand.update_thread.start()

            AsyncRunCommand.progress_thread = threading.Thread(target=self.show_progress)
            AsyncRunCommand.progress_thread.start()

        elif action == 'stop':
            self.stop_execution()

    def show_progress(self):
        i = 0
        frames = ['|', '/', '-', '\\']
        while AsyncRunCommand.running:
            if AsyncRunCommand.stop_event.is_set():
                break
            frame = frames[i % len(frames)]
            sublime.status_message(f'Running command... {frame}')
            AsyncRunCommand.stop_event.wait(0.1)
            i += 1
        sublime.status_message('Command execution finished')

    def stop_execution(self):
        print('Stopping execution')
        if AsyncRunCommand.running:
            AsyncRunCommand.stop_event.set()
            if AsyncRunCommand.process:
                AsyncRunCommand.process.terminate()
                AsyncRunCommand.process.wait(timeout=5)
            AsyncRunCommand.running = False
            if AsyncRunCommand.run_thread:
                AsyncRunCommand.run_thread.join(timeout=5)
            if AsyncRunCommand.update_thread:
                AsyncRunCommand.update_thread.join(timeout=5)
            if AsyncRunCommand.progress_thread:
                AsyncRunCommand.progress_thread.join(timeout=5)
            sublime.status_message('Command execution stopped')
        else:
            sublime.status_message('No command is running')

    def run_code_async(self, code):
        try:
            AsyncRunCommand.process = subprocess.Popen(
                # shlex.split(code),
                code,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=True,
                cwd=AsyncRunCommand.working_directory,
            )
            for line in AsyncRunCommand.process.stdout:
                if AsyncRunCommand.stop_event.is_set():
                    break
                AsyncRunCommand.output_queue.put(line)
            for line in AsyncRunCommand.process.stderr:
                if AsyncRunCommand.stop_event.is_set():
                    break
                AsyncRunCommand.output_queue.put(line)
            AsyncRunCommand.process.stdout.close()
            AsyncRunCommand.process.stderr.close()
            AsyncRunCommand.process.wait()
        except Exception as e:
            AsyncRunCommand.output_queue.put(f'Error running code: {str(e)}')
        finally:
            AsyncRunCommand.running = False
            AsyncRunCommand.output_queue.put(None)  # Signal end of output
            # if AsyncRunCommand.run_thread:
            # AsyncRunCommand.run_thread.join()
            if AsyncRunCommand.update_thread:
                AsyncRunCommand.update_thread.join(timeout=5)
            if AsyncRunCommand.progress_thread:
                AsyncRunCommand.progress_thread.join(timeout=5)

    def update_output(self):
        while True:
            try:
                line = AsyncRunCommand.output_queue.get(timeout=0.1)
                if line is None:  # End of output
                    self.view.run_command(
                        'insert_snippet',
                        {
                            'contents': '\n# ====================================== end ====================================== #\n'
                        },
                    )
                    break
                self.view.run_command('insert_snippet', {'contents': line})
            except queue.Empty:
                continue


class AsyncRunListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key == 'async_run_enabled':
            return AsyncRunCommand.running
        return None


class StopAsyncRun2Command(sublime_plugin.TextCommand):
    def run(self, edit):
        print('StopAsyncRunCommand triggered')
        AsyncRunCommand.stop_execution(self)


class ChangeDirCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('ChangeDirCommand triggered')
        AsyncRunCommand.set_working_directory(self)


# ===================================== THREDS ==================================== #


class SingleColumnCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command(
            'set_layout',
            {'cols': [0.0, 1.0], 'rows': [0.0, 1.0], 'cells': [[0, 0, 1, 1]]},
        )


class OpenScratchInNewLayoutCommand(sublime_plugin.WindowCommand):
    def run(self):
        num_groups = self.window.num_groups()

        if num_groups > 1:
            active_group = 1
        else:
            self.window.run_command(
                'set_layout',
                {
                    'cols': [0.0, 0.5, 1.0],
                    'rows': [0.0, 1.0],
                    'cells': [[0, 0, 1, 1], [1, 0, 2, 1]],
                },
            )
            active_group = 1
        new_view = self.window.new_file()
        self.window.set_view_index(new_view, active_group, len(self.window.views_in_group(active_group)))
        new_view.run_command('insert', {'characters': '# Title1\n'})
        self.window.focus_view(new_view)


# class OpenScratchInNewLayoutCommand(sublime_plugin.WindowCommand):
#     def run(self):
#         self.window.run_command(
#             "set_layout",
#             {
#                 "cols": [0.0, 0.5, 1.0],
#                 "rows": [0.0, 1.0],
#                 "cells": [
#                     [0, 0, 1, 1],  # Главный панель
#                     [1, 0, 2, 1],  # Вторая панель (для Scratch файла)
#                 ],
#             },
#         )

#         active_group = self.window.active_group()

#         # Create a new view in the active group
#         new_view = self.window.new_file()
#         self.window.set_view_index(
#             new_view, active_group, len(self.window.views_in_group(active_group))
#         )

#         # Insert text in the new view
#         new_view.run_command("insert", {"characters": "1111111"})


# class InsertTextCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#         # Вставьте текст в текущий файл
#         self.view.insert(edit, 0, "11111")


# class OpenScratchInSplitCommand(sublime_plugin.WindowCommand):
#     def run(self):
#         # Открыть новый Scratch файл
#         scratch = self.window.new_file()
#         scratch.set_name("Scratch")
#         scratch.set_scratch(True)

#         # Разделить текущее окно редактора на две части
# self.window.run_command(
#     "set_layout",
#     {
#         "cols": [0.0, 0.5, 1.0],
#         "rows": [0.0, 1.0],
#         "cells": [
#             [0, 0, 1, 1],  # Главный панель
#             [1, 0, 2, 1],  # Вторая панель (для Scratch файла)
#         ],
#     },
# )

#         # Переместить новый Scratch файл в правую панель
#         views = self.window.views()
#         scratch_view = [view for view in views if view.id() == scratch.id()][0]
#         self.window.focus_view(scratch_view)
#         self.window.run_command("move_file_to_group", {"group": 1})

#         # Вставить текст в новый файл
#         edit = scratch_view.begin_edit()
#         scratch_view.insert(edit, 0, "11111")
#         scratch_view.end_edit(edit)


# class OpenScratchAndInsertCommand(sublime_plugin.WindowCommand):
#     def run(self):
#         # Открыть новый Scratch файл
#         scratch = self.window.new_file()
#         scratch.set_name("Scratch")
#         scratch.set_scratch(True)

#         # Разделить окно редактора на две части
#         self.window.run_command(
#             "set_layout",
#             {
#                 "cols": [0.0, 0.5, 1.0],
#                 "rows": [0.0, 1.0],
#                 "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
#             },
#         )

#         # Получить вид для нового файла
#         view = scratch
#         if view:
#             # Вставить текст в новый файл
#             edit = view.begin_edit()
#             view.insert(edit, 0, "11111")
#             view.end_edit(edit)


# class OpenScratchAndInsertCommandWithHotkey(sublime_plugin.ApplicationCommand):
#     def run(self):
#         window = sublime.active_window()
#         if window:
#             window.run_command("open_scratch_and_insert")


class ExecuteSelectedTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                selected_text = self.view.substr(region)
                self.execute_command(edit, selected_text, region)

    def execute_command(self, edit, command_text, region):
        try:
            command = shlex.split(command_text)
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output = result.stdout
            self.view.insert(edit, region.end(), '\n' + output)
        except subprocess.CalledProcessError as e:
            # sublime.error_message(f"Ошибка выполнения команды: {e}")
            self.view.insert(edit, region.end(), '\n' + f'Ошибка выполнения команды: {e}')
        except Exception as e:
            # sublime.error_message(f"Произошла ошибка: {str(e)}")
            self.view.insert(edit, region.end(), '\n' + f'Произошла ошибка: {str(e)}')


class ExecuteToEndOfLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            line_region = self.view.line(region)
            command_text = self.view.substr(line_region)
            self.execute_command(edit, command_text, line_region)

    def execute_command(self, edit, command_text, region):
        # new = sublime.active_window().new_file()
        # new.set_scratch(True)
        try:
            command = shlex.split(command_text)
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            output = result.stdout + result.stderr
            # self.view.insert(edit, region.end(), "\n" + output)
            # new.insert(edit, 0, "\n" + output)

            window = self.view.window()
            num_groups = window.num_groups()
            if num_groups > 1:
                active_group = 1
            else:
                window.run_command(
                    'set_layout',
                    {
                        'cols': [0.0, 0.5, 1.0],
                        'rows': [0.0, 1.0],
                        'cells': [[0, 0, 1, 1], [1, 0, 2, 1]],
                    },
                )
                active_group = 1
            new_view = window.new_file()
            window.set_view_index(new_view, active_group, len(window.views_in_group(active_group)))
            new_view.run_command('insert_snippet', {'contents': output})
            window.focus_view(new_view)

            # new.run_command("append", {"characters": "\n" + output})
        except subprocess.CalledProcessError as e:
            sublime.error_message(f'Ошибка выполнения команды: {e}')
            # new.run_command("append", {"characters": "\n" + str(e)})
        except Exception as e:
            sublime.error_message(f'Произошла ошибка: {str(e)}')
            # new.run_command("append", {"characters": "\n" + str(e)})


class ExecuteToEndOfLine2Command(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            line_region = self.view.line(region)
            command_text = self.view.substr(line_region)
            self.execute_command(edit, command_text, line_region)

    def run_command(self, command_text):
        command = shlex.split(command_text)
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            output, error = process.communicate()
        return output + error

    def execute_command(self, edit, command_text, region):
        from concurrent.futures import ThreadPoolExecutor

        try:
            # command = shlex.split(command_text)
            # result = subprocess.run(command, capture_output=True, text=True, check=False)
            # output = result.stdout + result.stderr

            # output = run_command(command_text)

            window = self.view.window()
            num_groups = window.num_groups()
            if num_groups > 1:
                active_group = 1
            else:
                window.run_command(
                    'set_layout',
                    {
                        'cols': [0.0, 0.5, 1.0],
                        'rows': [0.0, 1.0],
                        'cells': [[0, 0, 1, 1], [1, 0, 2, 1]],
                    },
                )
                active_group = 1
            new_view = window.new_file()
            window.set_view_index(new_view, active_group, len(window.views_in_group(active_group)))
            window.focus_view(new_view)
            with ThreadPoolExecutor() as executor:
                future = executor.submit(self.run_command, command_text)
                output = future.result()
            new_view.run_command('insert_snippet', {'contents': output})

        except subprocess.CalledProcessError as e:
            sublime.error_message(f'Ошибка выполнения команды: {e}')
        except Exception as e:
            sublime.error_message(f'Произошла ошибка: {str(e)}')


# def plugin_loaded():
#     sublime.active_window().run_command("custom_buttons")


# class CustomButtonsCommand(sublime_plugin.WindowCommand):
#     def run(self):
#         print(1)
#         view = self.window.active_view()
#         html = """
#         <div style="padding: 10px;">
#             <a href="command1">Кнопка 1</a>
#             <a href="command2">Кнопка 2</a>
#         </div>
#         """
#         view.add_phantom(
#             "custom_buttons", sublime.Region(0), html, sublime.LAYOUT_INLINE
#         )

#     def on_navigate(self, href):
#         if href == "command1":
#             # Выполнить действие для кнопки 1
#             pass
#         elif href == "command2":
#             # Выполнить действие для кнопки 2
#             pass


# class InteractiveButtonsCommand(sublime_plugin.EventListener):
#     def __init__(self):
#         self.phantom_set = None

#     def on_selection_modified_async(self, view):
#         if self.phantom_set is None:
#             self.phantom_set = sublime.PhantomSet(view, "interactive_buttons")

#         cursor = view.sel()[0].end()
#         region = sublime.Region(cursor, cursor)

#         content = """
#             <body id="interactive-buttons">
#                 <style>
#                     #interactive-buttons {
#                         display: flex;
#                         gap: 5px;
#                     }
#                     .button {
#                         background-color: #4CAF50;
#                         border: none;
#                         color: white;
#                         padding: 5px 10px;
#                         text-align: center;
#                         text-decoration: none;
#                         display: inline-block;
#                         font-size: 12px;
#                         margin: 4px;
#                         cursor: pointer;
#                         border-radius: 3px;
#                     }
#                 </style>
#                 <a href="button1" class="button">Button 1</a>
#                 <a href="button2" class="button">Button 2</a>
#                 <a href="button3" class="button">Button 3</a>
#             </body>
#         """

#         phantom = sublime.Phantom(
#             region, content, sublime.LAYOUT_INLINE, self.on_navigate
#         )
#         self.phantom_set.update([phantom])

#     def on_modified_async(self, view):
#         if self.phantom_set:
#             self.phantom_set.update([])

#     def on_navigate(self, href):
#         if href == "button1":
#             sublime.message_dialog("Вы нажали кнопку 1")
#         elif href == "button2":
#             sublime.message_dialog("Вы нажали кнопку 2")
#         elif href == "button3":
#             sublime.message_dialog("Вы нажали кнопку 3")


# class PhantomHintCommand(sublime_plugin.EventListener):
#     def __init__(self):
#         self.phantom_set = None

#     def on_selection_modified_async(self, view):
#         if self.phantom_set is None:
#             self.phantom_set = sublime.PhantomSet(view, "phantom_hint")

#         cursor = view.sel()[0].end()
#         region = sublime.Region(cursor, cursor)

#         content = """
#             <body id="phantom-hint">
#                 <style>
#                     #phantom-hint {
#                         background-color: #ffff00;
#                         color: #000000;
#                         padding: 0 4px;
#                         border-radius: 3px;
#                     }
#                 </style>
#                 =>>>
#             </body>
#         """

#         phantom = sublime.Phantom(region, content, sublime.LAYOUT_INLINE)
#         self.phantom_set.update([phantom])

#     def on_modified_async(self, view):
#         if self.phantom_set:
#             self.phantom_set.update([])


class SelectToLeftQuoteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sel = view.sel()[0]
        line = view.line(sel)
        line_start = line.begin()
        cursor = sel.begin()

        left_text = view.substr(sublime.Region(line_start, cursor))
        quote_pos = max(left_text.rfind('"'), left_text.rfind("'"), left_text.rfind('"'))

        if quote_pos != -1:
            region = sublime.Region(line_start + quote_pos + 1, cursor)
            view.sel().clear()
            view.sel().add(region)
            view.erase(edit, region)


class SelectToRightQuoteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sel = view.sel()[0]
        line = view.line(sel)
        line_end = line.end()
        cursor = sel.end()

        right_text = view.substr(sublime.Region(cursor, line_end))
        quote_pos = min(
            pos
            for pos in [
                right_text.find('"'),
                right_text.find("'"),
                right_text.find('"'),
            ]
            if pos != -1
        )

        if quote_pos != -1:
            region = sublime.Region(cursor, cursor + quote_pos)
            view.sel().clear()
            view.sel().add(region)
            view.erase(edit, region)


# class PrintCursorLineCommand(sublime_plugin.EventListener):
#     def on_selection_modified(self, view):
#         selections = view.sel()
#         for selection in selections:
#             cursor_point = selection.begin()
#             cursor_line, _ = view.rowcol(cursor_point)
#             print(f"Cursor line: {cursor_line + 1}")


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


class InsertFormattedJsonCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        self.view.insert(edit, 0, text)


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


class ToggleCheckboxCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            line = self.view.line(region)
            text = self.view.substr(line)

            if text.startswith('[]'):
                self.view.replace(edit, line, f'[-]{text[2:]}')
            elif text.startswith('[-]'):
                self.view.replace(edit, line, f'[?]{text[3:]}')
            elif text.startswith('[?]'):
                self.view.replace(edit, line, f'[+]{text[3:]}')
            elif text.startswith('[+]'):
                self.view.replace(edit, line, f'{text[4:]}')
            elif (
                not text.startswith('[')
                and not text.startswith('[-]')
                and not text.startswith('[+]')
                and not text.startswith('[?]')
            ):
                self.view.replace(edit, line, f'[] {text}')


class MakeCompactTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                console = Console(width=110, record=True)
                ftext = Text(text)
                # text.stylize("bold magenta", 0, 6)
                console.print(ftext)
                self.view.replace(edit, selection, console.export_text())


class MakeArtHeaderCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                self.view.replace(edit, selection, text2art(text, font='alligator'))


class MakeHeaderCommand(sublime_plugin.TextCommand):
    # def set_format_text(self, text, left="=", right="=", length=110):
    def set_format_text(self, text, left='=', right='=', length=80):
        print('\n' in text)
        side_size = int((length - len(text)) / 2)
        if len(text) % 2 == 0:
            return f'# {side_size * left} {text} {(side_size - 1) * right} #'
        else:
            return f'# {side_size * left} {text} {side_size * right} #'

    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                self.view.replace(edit, selection, self.set_format_text(text))


class SlugifyTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                self.view.replace(edit, selection, slugify(text, separator='_'))


class WordsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # print(self.view.sel())
        # print(self.view.substr(self.view.sel()[0]))
        sel_w = self.view.substr(self.view.sel()[0])
        if sel_w:
            table = Table(title=sel_w.upper())
            table.add_column('#', justify='right', style='cyan', no_wrap=True)
            table.add_column('Char', justify='right', style='cyan', no_wrap=True)
            table.add_column('Value', style='magenta')
            chars_list = 'бвгдежзиклнопрстуфхцчшщэюя'
            word = sel_w
            res = []
            for k, lines in enumerate(chars_list, start=1):
                res.append(f'{k:<3}-> {lines + word[1:]}')
                table.add_row(str(k), lines.upper(), str(lines + word[1:]))
            new = sublime.active_window().new_file()
            console = Console(width=120, record=True)
            console.print(table)
            # new.insert(edit, 0, '\n'.join(res))
            new.insert(edit, 0, console.export_text())


class PanelCommand(sublime_plugin.TextCommand):
    def run(self, edit, title):
        self.sel_w = self.view.substr(self.view.sel()[0])
        if self.sel_w:
            region = self.view.sel()[0]
            text = Text(self.sel_w, justify='left')

            # Определение максимальной ширины текста
            max_text_width = max(len(line) for line in self.sel_w.splitlines())

            # Определение ширины заголовка
            title_width = len(title)

            # Вычисление итоговой ширины
            width = max(max_text_width, title_width) + 4  # +4 для отступов и рамки

            console = Console(width=width, record=True)
            console.print(Panel(text, title=title, width=width, highlight=True))

            self.view.replace(edit, region, console.export_text())
        else:
            print('not selected')


class PromCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel('Goto Line:', '-', self.on_done, None, None)

    def on_done(self, title):
        with contextlib.suppress(ValueError):
            self.window.active_view().run_command('panel', {'title': title})


class WrapRamkaCommand(sublime_plugin.TextCommand):
    """view.run_command("wrap_ramka")"""

    def run(self, edit):
        # Получение текста в выделенной области
        for region in self.view.sel():
            if not region.empty():
                s = self.view.substr(region)
                # Добавление рамки вокруг текста
                r = '-' * len(s)
                s = '\n'.join([f'+{r}+', f'|{s}|', f'+{r}+'])
                # Замена текста в выделенной области
                self.view.replace(edit, region, s)


class UnwrapRamkaCommand(sublime_plugin.TextCommand):
    """view.run_command("unwrap_ramka")"""

    def run(self, edit):
        # Получение текста в выделенной области
        for region in self.view.sel():
            if not region.empty():
                s = self.view.substr(region)
                # Удаление рамки вокруг текста
                s = '\n'.join(s.split('\n')[1:-1])
                s = s.replace('|', '')
                # Замена текста в выделенной области
                self.view.replace(edit, region, s)


class InsertDirectoryStructureCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                path = self.view.substr(region)
                if os.path.exists(path):
                    self.view.insert(edit, region.begin(), '\n' + self.get_structure(path))

    def get_structure(self, path):
        structure = ''
        for root, dirs, files in os.walk(path):
            structure += root + '\n'
            structure += '\t' + '\n\t'.join(dirs + files) + '\n'
        return structure


class GetPublicIpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        response = urllib.request.urlopen('https://api.ipify.org/').read()
        ip = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', response.decode())
        # self.view.insert(edit, 0, ip[0])
        self.view.run_command('insert', {'characters': ip[0]})


class ShowSystemProcessesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        output = subprocess.check_output('ps aux', shell=True).decode('utf-8')
        view = self.view.window().new_file()
        view.set_name('System Processes')
        view.set_scratch(True)
        view.insert(edit, 0, output)
