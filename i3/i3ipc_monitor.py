#!/run/media/izot/652aebd5-b153-4f9e-ba3d-2fb1b4d4b246/jek/TEMP/all_python/.venv_f/bin/python

import datetime
from datetime import timedelta

import i3ipc
from rich import pretty
from rich import print

pretty.install()
import pprint
from i3ipc import Con
from i3ipc.events import IpcBaseEvent

i3 = i3ipc.Connection()


def resize_window(i3, container_id, position_y: int = 25, height_width: int = 70):
    window = i3.get_tree().find_focused()
    workspace_name = window.workspace().name
    rect = window.workspace().rect
    new_window_width = rect.width / 2
    window_position = new_window_width / 2
    i3.command(f'move position {window_position:.0f} {rect.y + position_y}')
    i3.command(f'resize set {new_window_width:.0f} {rect.height - height_width}')
    i3.command(f'move container to workspace {workspace_name}')
    i3.command(f'[con_id="{container_id}"] resize set 50 ppt 90 ppt')


def focus_window(i3, container_id):
    """Float and focus current window."""
    i3.command(f'[con_id="{container_id}"] floating enable')
    i3.command(f'[con_id="{container_id}"] focus')


def move_container(i3, name, monitor, container_id=None):
    """Move give window to container and if container id is set focus to this container."""
    i3.command(f'move container to workspace {name}')
    i3.command(f'workspace {name}, move workspace to output {monitor}')
    if container_id:
        i3.command(f'[con_id="{container_id}"] focus')


# callback for when workspace focus changes
def on_workspace(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_output(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_mode(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_window(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_barconfig_update(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_binding(i3, e: IpcBaseEvent):
    print(e.__dict__)
    workspaces = i3.get_workspaces()
    focused_workspace = [w for w in workspaces if w.focused][0]
    focused_output = focused_workspace.output
    print('[focused_workspace]', focused_workspace)
    print('[focused_output]', focused_output)


def on_shutdown(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_tick(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_input(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_workspace_focus(i3, e: IpcBaseEvent):
    print(e.__dict__)
    print(e.current.name)


def on_workspace_init(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_workspace_empty(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_workspace_urgent(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_workspace_reload(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_workspace_rename(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_workspace_restored(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_workspace_move(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_window_new(i3, e: IpcBaseEvent):
    # print(json.dumps(e.__dict__, indent=4))
    # inspect(e.__dict__, methods=False, all=False)
    pprint.pprint(e.__dict__)
    title_name = e.ipc_data.get('container', {}).get('window_properties', {}).get('title', '')
    class_name = e.ipc_data.get('container', {}).get('window_properties', {}).get('class', '')
    instance = e.ipc_data.get('container', {}).get('window_properties', {}).get('instance', '')
    container_id = e.ipc_data.get('container', {}).get('id')
    if class_name == 'Firefox' and instance == 'Navigator':
        # move_container(i3, 'FOX', 'DisplayPort-2')
        i3.command(f'move container to workspace FOX')
        i3.command(f'workspace FOX, move workspace to output DisplayPort-2')
    elif class_name == 'Sublime_text' and instance == 'sublime_text':
        # move_container(i3, 'TEXT', 'DisplayPort-2')
        i3.command(f'move container to workspace TEXT')
        i3.command(f'workspace TEXT, move workspace to output DisplayPort-2')
    # if class_name == 'Pcmanfm':
    #     # move_container(i3, '2', 'DisplayPort-0')
    #     i3.command(f'move container to workspace 2')
    #     i3.command(f'workspace 2, move workspace to output DisplayPort-0')
    elif class_name == 'Slack':
        # move_container(i3, 'Slack', 'DisplayPort-2')
        i3.command(f'move container to workspace Slack')
        i3.command(f'workspace FOX, move workspace to output DisplayPort-2')
    elif class_name == 'jetbrains-pycharm-ce' and title_name.startswith('Terminal -'):
        # move_container(i3, 'CONSOLE', 'DisplayPort-2', container_id)
        i3.command(f'move container to workspace CONSOLE')
        i3.command(f'workspace CONSOLE, move workspace to output DisplayPort-2')
        i3.command(f'workspace CONSOLE, gaps inner all set 20')
        i3.command(f'[con_id="{container_id}"] focus')
    elif class_name == 'jetbrains-pycharm-ce' and title_name.startswith('Run -'):
        # move_container(i3, 'RUN', 'DisplayPort-2', container_id)
        i3.command(f'move container to workspace RUN')
        i3.command(f'workspace RUN, move workspace to output DisplayPort-2')
        i3.command(f'[con_id="{container_id}"] focus')
    elif class_name == 'jetbrains-pycharm-ce' and title_name.startswith('Debug -'):
        # move_container(i3, 'DEBUG', 'DisplayPort-2', container_id)
        i3.command(f'move container to workspace DEBUG')
        i3.command(f'workspace DEBUG, move workspace to output DisplayPort-2')
        i3.command(f'[con_id="{container_id}"] focus')
    if class_name == 'jetbrains-pycharm-ce' and title_name.startswith('win'):
        # focus_window(i3, container_id)
        i3.command(f'[con_id="{container_id}"] floating enable')
        i3.command(f'[con_id="{container_id}"] focus')
    elif (
        class_name == 'jetbrains-pycharm-ce'
        and title_name.startswith('Copy')
        or title_name.startswith('Select Target')
        or title_name.startswith('Rename')
    ):
        # focus_window(i3, container_id)
        i3.command(f'[con_id="{container_id}"] floating enable')
        i3.command(f'[con_id="{container_id}"] focus')
    elif class_name == 'steam_app_881100' and title_name.startswith('Noita'):
        # move_container(i3, 'NOITA', 'DisplayPort-0', container_id)
        i3.command(f'move container to workspace NOITA')
        i3.command(f'workspace NOITA, move workspace to output DisplayPort-0')
        i3.command(f'[con_id="{container_id}"] focus')
    elif class_name == 'Wine' and title_name.startswith('Session manager') and instance == 'heidisql.exe':
        # move_container(i3, 'SQL', 'DisplayPort-2')
        i3.command(f'move container to workspace SQL')
        i3.command(f'workspace SQL, move workspace to output DisplayPort-2')
        # focus_window(i3, container_id)
        i3.command(f'[con_id="{container_id}"] floating disable')
        i3.command(f'[con_id="{container_id}"] focus')
    elif title_name.startswith('HEIDI'):
        # move_container(i3, 'SQL', 'DisplayPort-2')
        i3.command(f'move container to workspace SQL')
        i3.command(f'workspace SQL, move workspace to output DisplayPort-2')
    elif (
        class_name == 'jetbrains-pycharm-ce'
        and title_name.startswith('Evaluate')
        and instance == 'jetbrains-pycharm-ce'
    ):
        # focus_window(i3, container_id)
        i3.command(f'[con_id="{container_id}"] floating enable')
        i3.command(f'[con_id="{container_id}"] focus')
        # resize_window(i3, container_id, 25, 70)
        window = i3.get_tree().find_focused()
        workspace_name = window.workspace().name
        rect = window.workspace().rect
        new_window_width = rect.width / 2
        window_position = new_window_width / 2
        i3.command(f'move position {window_position:.0f} {rect.y + 25}')
        i3.command(f'resize set {new_window_width:.0f} {rect.height - 70}')
        i3.command(f'move container to workspace {workspace_name}')
        i3.command(f'[con_id="{container_id}"] resize set 50 ppt 90 ppt')
    elif class_name == 'Sakura' and instance == 'sakura':
        # move_container(i3, 'TERM', 'DisplayPort-2', container_id)
        i3.command(f'move container to workspace TERM')
        i3.command(f'workspace TERM, move workspace to output DisplayPort-2')
        i3.command(f'[con_id="{container_id}"] focus')
    elif class_name == 'Gedit' and title_name.startswith('gedit') and instance == 'gedit':
        # focus_window(i3, container_id)
        i3.command(f'[con_id="{container_id}"] floating enable')
        i3.command(f'[con_id="{container_id}"] focus')
        # resize_window(i3, container_id, 25, 70)
        window = i3.get_tree().find_focused()
        workspace_name = window.workspace().name
        rect = window.workspace().rect
        new_window_width = rect.width / 2
        window_position = new_window_width / 2
        i3.command(f'move position {window_position:.0f} {rect.y + 25}')
        i3.command(f'resize set {new_window_width:.0f} {rect.height - 70}')
        i3.command(f'move container to workspace {workspace_name}')
        i3.command(f'[con_id="{container_id}"] resize set 50 ppt 90 ppt')
    elif class_name == 'Eog' and title_name.startswith('Image Viewer') and instance == 'eog':
        # focus_window(i3, container_id)
        i3.command(f'[con_id="{container_id}"] floating enable')
        i3.command(f'[con_id="{container_id}"] focus')
        # resize_window(i3, container_id, 25, 70)
        window = i3.get_tree().find_focused()
        workspace_name = window.workspace().name
        rect = window.workspace().rect
        new_window_width = rect.width / 2
        window_position = new_window_width / 2
        i3.command(f'move position {window_position:.0f} {rect.y + 25}')
        i3.command(f'resize set {new_window_width:.0f} {rect.height - 70}')
        i3.command(f'move container to workspace {workspace_name}')
        i3.command(f'[con_id="{container_id}"] resize set 50 ppt 90 ppt')
    elif class_name == 'TTT' and instance == 'sakura':
        # focus_window(i3, container_id)
        i3.command(f'[con_id="{container_id}"] floating enable')
        i3.command(f'[con_id="{container_id}"] focus')
        # resize_window(i3, container_id, 25, 70)
        window = i3.get_tree().find_focused()
        workspace_name = window.workspace().name
        rect = window.workspace().rect
        new_window_width = rect.width / 2
        window_position = new_window_width / 2
        i3.command(f'move position {window_position:.0f} {rect.y + 25}')
        i3.command(f'resize set {new_window_width:.0f} {rect.height - 70}')
        i3.command(f'move container to workspace {workspace_name}')
        i3.command(f'[con_id="{container_id}"] resize set 50 ppt 90 ppt')
    elif (
        class_name == 'Evince'
        and title_name.startswith('Document Viewer')
        and instance == 'evince'
        and not e.container.fullscreen_mode
    ):
        i3.command(f'[con_id="{container_id}"] fullscreen toggle')
    elif class_name == 'vlc' and title_name.startswith('VLC media player') and instance == 'vlc':
        # focus_window(i3, container_id)
        i3.command(f'[con_id="{container_id}"] floating enable')
        i3.command(f'[con_id="{container_id}"] focus')
        # resize_window(i3, container_id, 25, 70)
        window = i3.get_tree().find_focused()
        workspace_name = window.workspace().name
        rect = window.workspace().rect
        new_window_width = rect.width / 2
        window_position = new_window_width / 2
        i3.command(f'move position {window_position:.0f} {rect.y + 25}')
        i3.command(f'resize set {new_window_width:.0f} {rect.height - 70}')
        i3.command(f'move container to workspace {workspace_name}')
        i3.command(f'[con_id="{container_id}"] resize set 50 ppt 90 ppt')
    elif class_name == 'File-roller' and title_name.startswith('Archive Manager') and instance == 'file-roller':
        # focus_window(i3, container_id)
        i3.command(f'[con_id="{container_id}"] floating enable')
        i3.command(f'[con_id="{container_id}"] focus')
        # resize_window(i3, container_id, 25, 70)
        window = i3.get_tree().find_focused()
        workspace_name = window.workspace().name
        rect = window.workspace().rect
        new_window_width = rect.width / 2
        window_position = new_window_width / 2
        i3.command(f'move position {window_position:.0f} {rect.y + 25}')
        i3.command(f'resize set {new_window_width:.0f} {rect.height - 70}')
        i3.command(f'move container to workspace {workspace_name}')
        i3.command(f'[con_id="{container_id}"] resize set 50 ppt 90 ppt')


def on_window_close(i3, e: IpcBaseEvent):
    print(e.__dict__)


F1 = {}


def add_rules(key):
    F1[key] = datetime.datetime.utcnow()


def window_stop(key: str):
    if sss := F1.get(key):
        if datetime.datetime.utcnow() - sss <= timedelta(seconds=3):
            return False
        add_rules(key)
        return True
    add_rules(key)
    return True


def print_rules_item(focused: Con):
    print(
        f"elif focused.window_title == '{focused.window_title}' and focused.window_class == '{focused.window_class}' and focused.window_instance == '{focused.window_instance}' and window_stop(f'{focused.window_class}_{focused.window_instance}') and not focused.workspace().name == '{focused.window_class}':\n\tpass"
    )


def on_window_focus(i3, e: IpcBaseEvent):
    # pprint.pprint(e.__dict__)
    focused = i3.get_tree().find_focused()
    print_rules_item(focused)
    w = i3.get_tree().workspace()
    # print('[111]', focused.window)
    # print('[111]', focused.window_class)
    # print('[111]', focused.window_instance)
    # print('[111]', focused.window_title)
    # print('[111]', w)
    # title_name = e.ipc_data.get('container', {}).get('window_properties', {}).get('title', '')
    # class_name = e.ipc_data.get('container', {}).get('window_properties', {}).get('class', '')
    # instance = e.ipc_data.get('container', {}).get('window_properties', {}).get('instance', '')
    # container_id = e.ipc_data.get('container', {}).get('id')
    # if class_name == 'TelegramDesktop' and title_name.startswith('Telegram'):
    #     os.system('setxkbmap -layout ru,us, -option grp:alt_shift_toggle')
    # else:
    #     os.system('setxkbmap -layout us,ru, -option grp:alt_shift_toggle')
    if (
        focused.window_class == 'Firefox'
        and focused.window_instance == 'Navigator'
        and window_stop(f'{focused.window_class}_{focused.window_instance}')
        and not focused.workspace().name == 'Fox'
    ):
        i3.command(f'move container to workspace FOX')
        i3.command(f'workspace FOX, move workspace to output DisplayPort-2')
    elif (
        focused.window_class == 'Sublime_text'
        and focused.window_instance == 'sublime_text'
        and window_stop(f'{focused.window_class}_{focused.window_instance}')
        and not focused.workspace().name == 'TEXT'
    ):
        i3.command(f'move container to workspace TEXT')
        i3.command(f'workspace FOX, move workspace to output DisplayPort-2')
    elif (
        focused.window_class == 'TelegramDesktop'
        and focused.window_instance.startswith('Telegram')
        and window_stop(f'{focused.window_class}_{focused.window_instance}')
        and not focused.workspace().name == 'TEXT'
    ):
        i3.command(f'move container to workspace Telegram')
        i3.command(f'workspace Telegram, move workspace to output DisplayPort-2')
    elif (
        # focused.window_title == 'i3'
        focused.window_class == 'Pcmanfm'
        and focused.window_instance == 'pcmanfm'
        and window_stop(f'Pcmanfm_pcmanfm')
        and not focused.workspace().name == '2'
    ):
        i3.command(f'move container to workspace 2')
        i3.command(f'workspace 2, move workspace to output DisplayPort-0')
    elif (
        # focused.window_title == 'WinBox v3.31 (Addresses)'
        focused.window_class == 'Wine'
        and focused.window_instance == 'winbox.exe'
        and window_stop(f'Wine_winbox.exe')
        and not focused.workspace().name == 'Winbox'
    ):
        i3.command(f'move container to workspace Winbox')
        i3.command(f'workspace Winbox, move workspace to output DisplayPort-0')


def on_window_title(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_window_fullscreen_mode(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_window_move(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_window_floating(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_window_urgent(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_window_mark(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_shutdown_restart(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_shutdown_exit(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_input_added(i3, e: IpcBaseEvent):
    print(e.__dict__)


def on_input_removed(i3, e: IpcBaseEvent):
    print(e.__dict__)


# i3.on('workspace', on_workspace)
# i3.on('output', on_output)
# i3.on('mode', on_mode)
# i3.on('window', on_window)
# i3.on('barconfig_update', on_barconfig_update)

# i3.on('binding', on_binding) # 3

# i3.on('shutdown', on_shutdown)
# i3.on('tick', on_tick)
# i3.on('input', on_input)
# i3.on('workspace::focus', on_workspace_focus)
# i3.on('workspace::init', on_workspace_init)
# i3.on('workspace::empty', on_workspace_empty)
# i3.on('workspace::urgent', on_workspace_urgent)
# i3.on('workspace::reload', on_workspace_reload)
# i3.on('workspace::rename', on_workspace_rename)
# i3.on('workspace::restored', on_workspace_restored)
# i3.on('workspace::move', on_workspace_move)

i3.on('window::new', on_window_new)  # 1

# i3.on('window::close', on_window_close)

i3.on('window::focus', on_window_focus)  # 2

# i3.on('window::title', on_window_title)
# i3.on('window::fullscreen_mode', on_window_fullscreen_mode)
# i3.on('window::move', on_window_move)
# i3.on('window::floating', on_window_floating)
# i3.on('window::urgent', on_window_urgent)
# i3.on('window::mark', on_window_mark)
# i3.on('shutdown::restart', on_shutdown_restart)
# i3.on('shutdown::exit', on_shutdown_exit)
# i3.on('input::added', on_input_added)
# i3.on('input::removed', on_input_removed)
i3.main()
