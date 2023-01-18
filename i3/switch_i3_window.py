#!/run/media/izot/652aebd5-b153-4f9e-ba3d-2fb1b4d4b246/jek/TEMP/all_python/.venv_f/bin/python
import i3ipc
import os
import fire
import shelve


def sss(message: str):
    os.system(f"notify-send 'title' '{message}'")


class WorkspaceSwitcher:
    """bindsym $mod+Control+z exec "switch_i3_window.py switch Pycharm
    'workspace PyCharm'"."""

    def __init__(self):
        self.i3 = i3ipc.Connection()
        self.db = '/dev/shm/window.db'

    def switch(self, tag: str, command: str):
        """Switch to previous workspace or exec command."""
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

    def center_window(self):
        """
        The center_window() function is a method of the WorkspaceSwitcher class that is used to float and center the currently focused window in the i3 window manager.
        When the method is called, it uses the i3.get_tree().find_focused() method to get the currently focused window.
        It then checks if the window is already in floating mode (floating == 'user_on'), if so it disables the floating mode by executing the command 'floating disable'.
        If the window is not in floating mode, the method enables floating mode for the window by executing the command 'floating enable'.
        Then it gets the name of the workspace where the window is located and the rectangle of the workspace using a.workspace().name and a.workspace().rect respectively.
        The method then calculates the new width of the window to be half of the width of the workspace and new position of the window by dividing the new width by 2.
        Then it executes the command 'move position {window_position:.0f} {rect.y + 25}' to move the window to the new position.
        The method also resizes the window by executing the command 'resize set {new_window_width:.0f} {rect.height - 70}' to set the new width and height.
        It then focuses the window by executing the command '[con_id="{a.id}"] focus' and switches to the workspace where the window is located by executing the command 'workspace {workspace_name}'.
        Finally, the method uses the 'xdotool' command to move the mouse cursor to the top-left corner of the window.
        Note that this function is assuming that the width of the workspace is bigger than its height, otherwise it may not center the window as expected.
        """
        a = self.i3.get_tree().find_focused()
        if a.floating == 'user_on':
            a.command('floating disable')
            return
        workspace_name = a.workspace().name
        rect = a.workspace().rect
        a.command('floating enable')
        new_window_width = rect.width / 2
        window_position = new_window_width / 2
        a.command(f'move position {window_position:.0f} {rect.y + 25}')
        a.command(f'resize set {new_window_width:.0f} {rect.height - 70}')
        a.command(f'move container to workspace {workspace_name}')
        # a.command(f'[con_id="{a.id}"] resize set 50 ppt 50 ppt')
        a.command(f'[con_id="{a.id}"] focus')
        a.command(f'workspace {workspace_name}')
        # os.system(f'xdotool mousemove --window {a.id} 0 0')


if __name__ == '__main__':
    fire.Fire(WorkspaceSwitcher)
