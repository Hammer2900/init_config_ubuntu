import contextlib
import http.client
import json
import os
import queue
import shlex
import subprocess
import threading

import sublime
import sublime_plugin
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


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

class ChangeDirCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('ChangeDirCommand triggered')
        AsyncRunCommand.set_working_directory(self)

