import sublime
import sublime_plugin

"""
**Bracket Highlighter** — это плагин для **Sublime Text**, который подсвечивает парные скобки при наведении курсора мыши.
Плагин отслеживает событие `on_hover`, проверяет символ под курсором и, если это одна из поддерживаемых скобок `()`, `[]`, `{}` или `||`, запускает алгоритм поиска соответствующей пары в тексте.
Для корректной работы с вложенными конструкциями используется стек: если курсор находится на открывающей скобке, поиск выполняется вперёд до нахождения соответствующей закрывающей;
если на закрывающей — поиск идёт назад до соответствующей открывающей. Когда пара найдена, обе скобки подсвечиваются в редакторе с помощью `view.add_regions` и стиля `DRAW_SOLID_UNDERLINE`,
что визуально выделяет их подчёркиванием без изменения фона. Например, в коде `result = (a + (b * (c + d)))` при наведении курсора на первую `(` плагин подсветит соответствующую последнюю `)`,
корректно учитывая вложенные скобки.
"""

class BracketHighlighterListener(sublime_plugin.EventListener):
    def __init__(self):
        self.bracket_pairs = {'(': ')', '[': ']', '{': '}', '|': '|'}

    def on_hover(self, view, point, hover_zone):
        view.erase_regions('bracket_highlighter')
        if hover_zone != sublime.HOVER_TEXT:
            return
        regions = self.find_matching_brackets(view, point)
        if regions:
            view.add_regions(
                'bracket_highlighter',
                regions,
                'bracket_highlighter',
                '',
                sublime.DRAW_SOLID_UNDERLINE | sublime.DRAW_NO_FILL,
            )

    def find_matching_brackets(self, view, point):
        char_at_point = view.substr(point)
        opening_char_type = None
        target_closing_char = None
        search_direction = 0
        if char_at_point in self.bracket_pairs:
            opening_char_type = char_at_point
            target_closing_char = self.bracket_pairs[char_at_point]
            search_direction = 1
        elif char_at_point in self.bracket_pairs.values():
            target_closing_char = char_at_point
            for k, v in self.bracket_pairs.items():
                if v == char_at_point:
                    opening_char_type = k
                    break
            if opening_char_type is None:
                return None
            search_direction = -1
        else:
            return None
        stack = []
        current_scan_point = point
        limit = view.size()
        while 0 <= current_scan_point < limit:
            current_char_scanned = view.substr(current_scan_point)
            if search_direction == 1:
                if current_char_scanned == opening_char_type:
                    stack.append(current_scan_point)
                elif current_char_scanned == target_closing_char:
                    if not stack:
                        return None
                    opened_at_pos = stack.pop()
                    if opened_at_pos == point:
                        return [
                            sublime.Region(point, point + 1),
                            sublime.Region(current_scan_point, current_scan_point + 1),
                        ]
            elif search_direction == -1:
                if current_char_scanned == target_closing_char:
                    stack.append(current_scan_point)
                elif current_char_scanned == opening_char_type:
                    if not stack:
                        return None
                    closed_at_pos = stack.pop()
                    if closed_at_pos == point:
                        return [
                            sublime.Region(current_scan_point, current_scan_point + 1),
                            sublime.Region(point, point + 1),
                        ]
            else:
                return None
            current_scan_point += search_direction
            if search_direction == 0:
                break
        return None


def plugin_loaded():
    sublime.load_settings('Preferences.sublime-settings').set(
        'bracket_highlighter_style',
        {'scope': 'bracket_highlighter', 'color': '#FFFFFF', 'style': 'solid'},
    )
