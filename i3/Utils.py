#!/usr/bin/env /home/izot/.local/share/virtualenvs/test_python3-_8u9lZwJ/bin/python

import webview
import i3ipc

i3 = i3ipc.Connection()
root = i3.get_tree()
if finding := root.find_named('Utils1'):
    root.command('workspace Utils')
    root.command(f'[con_id={finding[0].id}] focus')
else:
    root.command('workspace Utils')
    webview.create_window('Utils1', 'https://hammer2900.github.io/')
    webview.start()
