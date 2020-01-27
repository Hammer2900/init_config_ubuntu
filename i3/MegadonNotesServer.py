#!/usr/bin/env /home/izot/.local/share/virtualenvs/test_python3-_8u9lZwJ/bin/python

import webview
import i3ipc

i3 = i3ipc.Connection()
root = i3.get_tree()
finding = root.find_named('MegadonNotesServer1')
if finding:
    root.command('workspace Notes')
    root.command('[con_id=%s] focus' % finding[0].id)
else:
    root.command('workspace Notes')
    webview.create_window('MegadonNotesServer1', 'http://91.241.167.37:99/')
    webview.start()



