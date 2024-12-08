#!/run/media/izot/652aebd5-b153-4f9e-ba3d-2fb1b4d4b246/jek/TEMP/all_python/.venv_f/bin/python
import os
import re
import shelve
import tkinter as tk
from subprocess import PIPE, Popen

import fire
import i3ipc


def sss(message: str):
    os.system(f"notify-send 'title' '{message}'")


def get_activityname():
    root = Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=PIPE)
    stdout, stderr = root.communicate()
    m = re.search(b'^_NET_ACTIVE_WINDOW.* ([\w]+)$', stdout)

    if m is not None:
        window_id = m[1]

        windowname = None
        window = Popen(['xprop', '-id', window_id, 'WM_NAME'], stdout=PIPE)
        stdout, stderr = window.communicate()
        wmatch = re.match(b'WM_NAME\(\w+\) = (?P<name>.+)$', stdout)
        if wmatch is not None:
            windowname = wmatch['name'].decode('UTF-8').strip('"')

        processname1, processname2 = None, None
        process = Popen(['xprop', '-id', window_id, 'WM_CLASS'], stdout=PIPE)
        stdout, stderr = process.communicate()
        pmatch = re.match(b'WM_CLASS\(\w+\) = (?P<name>.+)$', stdout)
        if pmatch is not None:
            processname1, processname2 = pmatch['name'].decode('UTF-8').split(', ')
            processname1 = processname1.strip('"')
            processname2 = processname2.strip('"')

        return {
            'windowname': windowname,
            'processname1': processname1,
            'processname2': processname2,
        }

    return {'windowname': None, 'processname1': None, 'processname2': None}


class WorkspaceSwitcher:
    """
    App manage switching between i3 workspaces and executing commands.

    Provides methods for switching to a specific workspace, remembering the
    previous workspace, and centering the currently focused window.

    Example usage from i3 config:
    bindsym $mod+Control+z exec "switch_i3_window.py switch Pycharm 'workspace PyCharm'"
    """

    def __init__(self):
        """Initializes the WorkspaceSwitcher with an i3 connection and a shelf for persistent storage."""
        self.i3 = i3ipc.Connection()
        self.db = '/dev/shm/window.db'

    def window_name(self):
        """
        Displays window information in a new Tkinter window.

        Retrieves active window information using `get_activityname()` and displays
        it in a formatted text box within a new window.  The information includes:

        - Window Title
        - Process Name (two variations)
        - Suggested Sway configuration snippets for:
            - Assigning tags based on class and title.
            - Applying floating mode, border, and title format.
            - Moving the window to a specific workspace and output.
       """
        root = tk.Tk()

        label = tk.Label(root, text='Window information.')
        label2 = tk.Text(root, width=120, height=30, bg='darkgreen', padx=10, pady=10)
        label.pack(padx=60, pady=10)
        label2.pack(padx=10, pady=10)
        a = get_activityname()
        label2.insert(tk.INSERT, 'windowname: \n')
        label2.insert(tk.INSERT, a['windowname'] + '\n\n')
        label2.insert(tk.INSERT, '')

        label2.insert(tk.INSERT, 'processname1: \n')
        label2.insert(tk.INSERT, a['processname1'] + '\n\n')
        label2.insert(tk.INSERT, '')

        label2.insert(tk.INSERT, 'processname2: \n')
        label2.insert(tk.INSERT, a['processname2'] + '\n\n')
        label2.insert(tk.INSERT, '')

        label2.insert(tk.INSERT, 'Class to tag: \n')
        label2.insert(tk.INSERT, f'assign [class="{a["processname1"]}"] → Test\n')
        label2.insert(tk.INSERT, f'assign [class="{a["processname2"]}"] → Test2\n')
        label2.insert(tk.INSERT, f'assign [title="{a["windowname"]}"] → Title\n')
        label2.insert(tk.INSERT, '---\n')
        label2.insert(tk.INSERT, f'for_window [class="{a["processname1"]}"] floating enable border pixel 3\n')
        label2.insert(tk.INSERT, f'for_window [class="{a["processname1"]}"] title_format "* %title *"\n')
        label2.insert(
            tk.INSERT,
            f'for_window [title="{a["windowname"]}"] move to workspace $ws9, focus, move workspace to output $hdm0\n'
        )
        label2.insert(tk.INSERT, '---\n')

        root.mainloop()

    def switch(self, tag: str, command: str):
        """
        Switches to a specified workspace or executes a command.

        If the current workspace matches the provided tag and a previous
        workspace is stored, it switches to the previous workspace. Otherwise,
        it stores the current workspace as the previous one and executes
        the provided command.  The previous workspace is stored persistently.

        Args:
            tag (str): The tag of the target workspace.
            command (str): The i3 command to execute if the current workspace
                           does not match the tag. Typically 'workspace <workspace_name>'.
        """
        with shelve.open(self.db) as f:
            workspaces = self.i3.get_workspaces()
            focused_workspace = [w for w in workspaces if w.focused][0]
            current_workspace = focused_workspace.name
            print('[focused_workspace]', current_workspace)
            print('[previous_workspace]', f.get('previous_workspace'))
            previous_workspace = f.get('previous_workspace')
            if previous_workspace and tag == current_workspace:
                self.i3.command(f'workspace {previous_workspace}')
            else:
                f['previous_workspace'] = current_workspace
                self.i3.command(command)

    def center_window(self, width=800, height=1000):  # added width and height parameters
        """
        Floats and centers the window to the specified width and height. Default is 800x1000.
        """
        a = self.i3.get_tree().find_focused()
        if a.floating == 'user_on':
            a.command('floating disable')
            return

        workspace_name = a.workspace().name
        rect = a.workspace().rect

        a.command('floating enable')

        # Use provided width and height
        a.command(f'resize set {width} {height}')

        # Center the window based on provided dimensions
        window_position_x = (rect.width - width) / 2
        window_position_y = (rect.height - height) / 2
        a.command(f'move position {window_position_x:.0f} {window_position_y:.0f}')

        a.command(f'move container to workspace {workspace_name}')
        a.command(f'[con_id="{a.id}"] focus')
        a.command(f'workspace {workspace_name}')


if __name__ == '__main__':
    fire.Fire(WorkspaceSwitcher)
