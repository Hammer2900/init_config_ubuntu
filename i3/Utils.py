#!/usr/bin/env /home/izot/.local/share/virtualenvs/test_python3-_8u9lZwJ/bin/python

import webview
import i3ipc

i3 = i3ipc.Connection()
root = i3.get_tree()
finding = root.find_named('Utils1')
if finding:
    root.command('workspace Utils')
    root.command('[con_id=%s] focus' % finding[0].id)
else:
    root.command('workspace Utils')
    webview.create_window('Utils1', 'https://hammer2900.github.io/')
    webview.start()



