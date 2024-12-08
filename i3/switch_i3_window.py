#!/run/media/izot/652aebd5-b153-4f9e-ba3d-2fb1b4d4b246/jek/TEMP/all_python/.venv_f/bin/python
import i3ipc
import os
import fire
import shelve


def sss(message: str):
    os.system(f"notify-send 'title' '{message}'")


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

    def center_window(self):
        """
        Floats and centers the currently focused window within its workspace.

        If the window is already floating, it disables floating mode. Otherwise,
        it enables floating mode, calculates the center position of the
        workspace, moves and resizes the window to be centered, and then
        refocuses the window.  It assumes the workspace is wider than it is tall.
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
