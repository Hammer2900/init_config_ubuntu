import sublime
import sublime_plugin
import re

"""
**AlignCommentsCommand** — это команда плагина для **Sublime Text**, которая автоматически выравнивает комментарии в коде по одному столбцу.
Команда анализирует выделенный текст (или весь файл, если выделения нет), построчно ищет комментарии вида `#` или `--` с помощью регулярного выражения,
разделяет строку на отступ, код и текст комментария, после чего рассчитывает позицию комментария так, чтобы он начинался не раньше минимального расстояния от кода
(`min_spacing`) и стремился к заданному столбцу (`target_column`, по умолчанию 70). Если строка содержит только комментарий без кода, он выравнивается непосредственно
к целевому столбцу; если же комментарий стоит после кода, между кодом и комментарием добавляется необходимое количество пробелов для аккуратного вертикального выравнивания.
Например, строки `x = 10 # value` и `long_variable = 20 # another value` после выполнения команды будут преобразованы так, чтобы оба комментария начинались примерно в одном столбце, что делает код визуально более аккуратным и читаемым.
"""


class AlignCommentsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        min_spacing = 2
        target_column = 70
        regions = self.view.sel()
        if not regions or all(region.empty() for region in regions):
            regions = [sublime.Region(0, self.view.size())]
        for region in regions:
            text = self.view.substr(region)
            lines = text.split('\n')
            modified_lines = []
            for line in lines:
                match = re.match(r'(\s*)(.*?)(#|--)\s*(.*)', line)
                if match:
                    indent, code, comment_char, comment_text = match.groups()
                    code = code.rstrip()
                    if not code:
                        spaces_needed = target_column
                        aligned_line = ' ' * spaces_needed + comment_char + ' ' + comment_text.strip()
                        modified_lines.append(aligned_line)
                    else:
                        code_length = len(indent + code)
                        comment_pos = max(code_length + min_spacing, target_column)
                        spaces_needed = comment_pos - code_length
                        aligned_line = indent + code + ' ' * spaces_needed + comment_char + ' ' + comment_text.strip()
                        modified_lines.append(aligned_line)
                else:
                    modified_lines.append(line)
            self.view.replace(edit, region, '\n'.join(modified_lines))
