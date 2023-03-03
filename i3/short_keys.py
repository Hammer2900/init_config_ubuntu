#!/run/media/izot/652aebd5-b153-4f9e-ba3d-2fb1b4d4b246/jek/TEMP/all_python/.venv_f/bin/python
import contextlib
import os
import time

import fire
import sh
from pynput import keyboard


class LeftCtrlTimeAction:
    def __init__(self, threshold: float = 0.5):
        self.ctrl_last_time = 0
        self.ctrl_count = 0
        self.threshold = threshold

    def check(self):
        if time.time() - self.ctrl_last_time < self.threshold:
            self.ctrl_count += 1
        else:
            self.ctrl_count = 1
        self.ctrl_last_time = time.time()

        if self.ctrl_count == 2:
            os.system('xdotool key ctrl+c')
            self.ctrl_count = 0


class LeftAltTimeAction:
    def __init__(self, threshold: float = 0.5):
        self.ctrl_last_time = 0
        self.ctrl_count = 0
        self.threshold = threshold

    def check(self):
        if time.time() - self.ctrl_last_time < self.threshold:
            self.ctrl_count += 1
        else:
            self.ctrl_count = 1
        self.ctrl_last_time = time.time()

        if self.ctrl_count == 2:
            sh.xdotool.key('--clearmodifiers', 'Shift+Insert')
            self.ctrl_count = 0


class RemapKeyBindingsToFastUse:
    __keys_list = {keyboard.Key.ctrl: LeftCtrlTimeAction(), keyboard.Key.alt_l: LeftAltTimeAction()}

    def __on_press(self, key):
        with contextlib.suppress(AttributeError):
            if k := self.__keys_list.get(key):
                k.check()

    def run(self):
        with keyboard.Listener(on_press=self.__on_press) as listener:
            listener.join()


if __name__ == '__main__':
    fire.Fire(RemapKeyBindingsToFastUse)
