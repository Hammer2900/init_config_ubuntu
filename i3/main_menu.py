#!/run/media/izot/652aebd5-b153-4f9e-ba3d-2fb1b4d4b246/jek/TEMP/all_python/.venv_f/bin/python
import re
import subprocess

import fire
from rofi import Rofi


class RofiCommands:
    """
    Class provides several functions to control different actions using the python-rofi library.

    pip install python-rofi
    """

    def __init__(self):
        """
        This method initializes an instance of the RofiCommands class by creating a Rofi object with
        specified parameters: fullscreen=False and exit_hotkeys=('Alt+F4', 'Control+q').
        """
        self._r = Rofi(fullscreen=False, exit_hotkeys=('Alt+F4', 'Control+q'))

    def _cmd(self, commands: list):
        """
        This method takes a list of commands and returns the output of the commands
        after executing it using the subprocess.check_output method.
        """
        return subprocess.check_output(commands).decode('utf-8')

    def _cmd_background(self, commands: list):
        """
        This method takes a list of commands and starts a new process to execute the commands
        in the background using the subprocess.Popen method."""
        return subprocess.Popen(commands)

    def _find_all_sinks(self):
        """
        This method returns a dict of all available sound sinks by executing the wpctl command and parsing the output.
        """
        status_str = self._cmd(['wpctl', 'status'])
        start = status_str.index('Sinks:')
        end = status_str.index('Sink endpoints:')
        index_ = status_str[start:end]
        return {name: id.replace('.', '') for id, name in re.findall(r'(\d+.) (.+)', index_) if 'Radeon' not in name}

    def _switch_sinks(self, id: str):
        """This method takes a str id and switches to the specified sound sink by executing the wpctl command."""
        return self._cmd(['wpctl', 'set-default', id])

    def _monitor_layout_3(self):
        self._cmd(
            [
                'xrandr',
                '--output',
                'DisplayPort-0',
                '--primary',
                '--mode',
                '1920x1080',
                '--pos',
                '1920x0',
                '--rotate',
                'normal',
                '--output',
                'DisplayPort-1',
                '--off',
                '--output',
                'DisplayPort-2',
                '--mode',
                '1920x1080',
                '--pos',
                '3849x0',
                '--rotate',
                'normal',
                '--output',
                'HDMI-A-0',
                '--mode',
                '1920x1080',
                '--pos',
                '0x0',
                '--rotate',
                'normal',
                '--output',
                'DVI-D-0',
                '--off',
            ]
        )

    def _monitor_layout_2(self):
        self._cmd(
            [
                'xrandr',
                '--output',
                'DisplayPort-0',
                '--primary',
                '--mode',
                '1920x1080',
                '--pos',
                '0x0',
                '--rotate',
                'normal',
                '--output',
                'DisplayPort-1',
                '--off',
                '--output',
                'DisplayPort-2',
                '--mode',
                '1920x1080',
                '--pos',
                '1920x0',
                '--rotate',
                'normal',
                '--output',
                'HDMI-A-0',
                '--off',
                '--output',
                'DVI-D-0',
                '--off',
            ]
        )

    def vlc_show_menu(self):
        """
        This method shows a menu to enter the URL or magnet link for a video,
        and plays the video using vlc if the input is a valid URL or magnet link.
        """
        name = self._r.text_entry('Paste url or magnet: ')
        if 'youtube' in name:
            self._cmd_background(['vlc', name])
        elif 'magnet' in name:
            self._cmd_background(['vlc', f'"{name}"'])

    def show_i3_config_menu(self):
        """This method opens the i3 configuration file in gedit to edit it."""
        self._cmd_background(['gedit', '/home/izot/.config/i3/config'])

    def sound_output_menu(self):
        """
        This method shows a menu of available sound sinks, and switches to the selected sink.
        The menu is displayed using the python-rofi library.
        """
        dict_sinks = self._find_all_sinks()
        options = list(dict_sinks)
        index, key = self._r.select('Please choice sinks', options)
        # self._switch_sinks(dict_sinks[options[index]])
        if index != -1:
            self._switch_sinks(dict_sinks[options[index]])
            self.sound_output_menu()
        else:
            print(
                '[empty]',
            )

    def monitor_output_menu(self):
        """
        This method shows a menu of available monitor layouts, and sets the selected layout.
        The menu is displayed using the python-rofi library.
        """
        dict_sinks = {'3 monitors': self._monitor_layout_3, '2 monitors': self._monitor_layout_2}
        options = list(dict_sinks)
        index, key = self._r.select('Please choice sinks', options)
        if index != -1:
            dict_sinks[options[index]]()
            self.monitor_output_menu()
        else:
            print('[empty]')

    def start_menu(self):
        """
        This method shows a menu of available actions, and executes the selected action.
        The menu is displayed using the python-rofi library.
        """
        actions_list = {
            'sound output': self.sound_output_menu,
            'monitor output': self.monitor_output_menu,
            'rztk parse': self.sound_output_menu,
            'mute': self.sound_output_menu,
            'ssh': self.sound_output_menu,
            'vlc': self.vlc_show_menu,
            'i3 config': self.show_i3_config_menu,
        }
        options = list(actions_list)
        index, key = self._r.select('Please choice action', options)
        print('[-]', index, key)
        print('[-]', actions_list[options[index]])
        if index != -1:
            actions_list[options[index]]()
        else:
            print(
                '[empty]',
            )


if __name__ == '__main__':
    fire.Fire(RofiCommands)
