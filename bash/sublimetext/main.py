import sublime
import sublime_plugin
import os
import re
import urllib.request
import subprocess
import contextlib
import json
import pprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich import print, pretty, inspect
from slugify import slugify
from art import text2art
import pretty_errors


# class PrintCursorLineCommand(sublime_plugin.EventListener):
#     def on_selection_modified(self, view):
#         selections = view.sel()
#         for selection in selections:
#             cursor_point = selection.begin()
#             cursor_line, _ = view.rowcol(cursor_point)
#             print(f"Cursor line: {cursor_line + 1}")


class TextRichTableCommand(sublime_plugin.TextCommand):
    def parse_input(self, input_str):
        rows = input_str.strip().split('\n')
        data = []
        for row in rows:
            cols = row.split(' - ')
            data.append(cols)
        return data

    def run(self, edit):
        for selection in self.view.sel():
            if not selection.empty():
                text = self.view.substr(selection)
                table = Table(show_header=False, expand=True, padding=0, show_lines=True)
                table.add_column('', justify='center')
                table.add_column('', justify='center')
                for row in self.parse_input(text):
                    table.add_row(*row)
                console = Console(width=90, record=True)
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
        split_sentences = [x.split(':') for x in text.split('\n')]
        max_head = max([len(x[0]) for x in split_sentences])
        max_tail = max([len(x[1]) for x in split_sentences])
        return '\n'.join([f'{x[0].ljust(max_head)} : {x[1].ljust(max_tail)}' for x in split_sentences])

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

                text = self.view.substr(selection)

                try:
                    res = json.loads(text)
                except json.decoder.JSONDecodeError:
                    res = eval(text)

                # format_text = pprint.pformat(res)
                format_text = json.dumps(res, indent=4)

                new.insert(edit, 0, format_text)


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
            new = sublime.active_window().new_file()
            new.set_scratch(True)
            console = Console(width=120, record=True)
            text = Text(self.sel_w, justify='left')
            console.print(Panel(text, title=title, width=120, highlight=True))
            new.insert(edit, 0, console.export_text())
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
