import sublime
import sublime_plugin
from art import text2art
from rich import print
from rich.console import Console
from rich.text import Text
from slugify import slugify


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
