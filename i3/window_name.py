#!/mnt/w1/jek/TEMP/all_python/.venv/bin/python
import re
import tkinter as tk
from subprocess import PIPE, Popen


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
    tk.INSERT, f'for_window [title="{a["windowname"]}"] move to workspace $ws9, focus, move workspace to output $hdm0\n'
)
label2.insert(tk.INSERT, '---\n')

root.mainloop()
