import contextlib
import sublime
import sublime_plugin
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print, pretty, inspect


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
            console = Console(width=120, record=True)
            console.print(Panel(self.sel_w, title=title, width=120, highlight=True))
            new.insert(edit, 0, console.export_text())
        else:
            print('not selected')


class PromCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel('Goto Line:', '-', self.on_done, None, None)

    def on_done(self, title):
        with contextlib.suppress(ValueError):
            self.window.active_view().run_command('panel', {'title': title})
