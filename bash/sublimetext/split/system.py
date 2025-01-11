import os
import re
import shlex
import subprocess
import urllib.request
from datetime import datetime, timezone, timedelta

import sublime
import sublime_plugin


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
