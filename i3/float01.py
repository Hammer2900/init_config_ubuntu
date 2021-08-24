#!/mnt/w1/jek/TEMP/all_python/.venv/bin/python
import os

import i3ipc

i3 = i3ipc.Connection()


def center_window():
    """
    Float and center window, i3wm.
    :return:
    """
    a = i3.get_tree().find_focused()
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


center_window()
