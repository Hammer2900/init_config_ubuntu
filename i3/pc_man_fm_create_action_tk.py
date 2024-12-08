#!/run/media/izot/652aebd5-b153-4f9e-ba3d-2fb1b4d4b246/jek/TEMP/init_config_ubuntu/.venv/bin/python
import os
import tkinter as tk

import fire


class TkFormAction:
    """
    A class to create a Tkinter form for collecting a script name and path,
    and then generating a desktop file for that script in the user's
    file manager actions directory.
    """
    def __init__(self):
        self._root = tk.Tk()
        self._root.title('Name and Path Form')

        self._name_label = tk.Label(self._root, text='Name:')
        self._name_entry = tk.Entry(self._root)
        self._path_label = tk.Label(self._root, text='Path:')
        self._path_entry = tk.Entry(self._root, width=110)
        self._message_label = tk.Label(self._root, text='', fg='red')

        ok_button = tk.Button(self._root, text='OK', command=self.__on_ok_click)
        exit_button = tk.Button(self._root, text='EXIT', command=self.__on_exit_click)

        self._name_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self._name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self._path_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self._path_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self._message_label.grid(row=2, columnspan=2, padx=5, pady=5)

        ok_button.grid(row=2, column=0, padx=5, pady=5)
        exit_button.grid(row=2, column=3, padx=5, pady=5)

        self._root.columnconfigure(1, weight=1)

    def __on_ok_click(self):
        name = self._name_entry.get()
        path = self._path_entry.get()
        if not name:
            self._message_label.config(text='Please enter a name.')

        else:
            self._message_label.config(text='')
            print(f'Name: {name}, Path: {path}')
            self.create_desktop_file(name, path)
            self._root.destroy()

    def __on_exit_click(self):
        self._root.destroy()

    def create_desktop_file(self, script_name, script_path):
        """
        Creates a desktop file for the given script.

        Args:
            script_name: The name of the script.
            script_path: The full path to the script.
        """
        desktop_file_content = f"""[Desktop Entry]
Type=Action
Name={script_name}
Icon=python
Profiles=profile-zero;

[X-Action-Profile profile-zero]
Exec={script_path} %f
MimeType=x-directory/normal;inode/directory;
"""

        actions_dir = os.path.expanduser('~/.local/share/file-manager/actions/')
        os.makedirs(actions_dir, exist_ok=True)

        desktop_file_path = os.path.join(actions_dir, f'{script_name}.desktop')

        with open(desktop_file_path, 'w') as desktop_file:
            desktop_file.write(desktop_file_content)

        print(f'Desktop file created at: {desktop_file_path}')

    def run(self, path: str = 'paste path to exec script'):
        self._path_entry.insert(0, path)
        self._root.mainloop()


if __name__ == '__main__':
    fire.Fire(TkFormAction)
