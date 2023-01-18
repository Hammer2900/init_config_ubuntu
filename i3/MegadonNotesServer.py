#!/mnt/w1/jek/TEMP/all_python/.venv/bin/python

import webview
import i3ipc

i3 = i3ipc.Connection()
root = i3.get_tree()
if finding := root.find_named('MegadonNotesServer1'):
    root.command('workspace Notes')
    root.command(f'[con_id={finding[0].id}] focus')
else:
    root.command('workspace Notes')
    webview.create_window('MegadonNotesServer1', 'http://91.241.167.37:99/')
    webview.start()
