import i3ipc

i3 = i3ipc.Connection()


def adjust_windows(workspace):
    windows = workspace.descendants()
    floating_windows = [win for win in windows if win.floating == 'user_on']
    focused = workspace.find_focused()

    if len(windows) == 2:
        focused.command('layout toggle split')
    elif len(floating_windows) == 0:
        focused.command('floating enable, resize set 1500 800, move position center')
    else:
        floating_win = floating_windows[0]

        if focused.id != floating_win.id:
            floating_win.command('floating disable')
            focused.command('floating enable, resize set 1500 800, move position center')


def on_window_focus(i3, event):
    focused = i3.get_tree().find_focused()
    workspace = focused.workspace()

    if workspace and workspace.name == 'TEXT':
        adjust_windows(workspace)


i3.on(i3ipc.Event.WINDOW_FOCUS, on_window_focus)
i3.main()
