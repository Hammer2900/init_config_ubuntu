#!/mnt/w1/jek/TEMP/all_python/.venv/bin/python
import re
from subprocess import PIPE, Popen

from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table


def get_activity_name():
    root = Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=PIPE)
    stdout, stderr = root.communicate()
    m = re.search(b'^_NET_ACTIVE_WINDOW.* ([\w]+)$', stdout)

    if m is not None:

        window_id = m.group(1)

        windowname = None
        window = Popen(['xprop', '-id', window_id, 'WM_NAME'], stdout=PIPE)
        stdout, stderr = window.communicate()
        wmatch = re.match(b'WM_NAME\(\w+\) = (?P<name>.+)$', stdout)
        if wmatch is not None:
            windowname = wmatch.group('name').decode('UTF-8').strip('"')

        processname1, processname2 = None, None
        process = Popen(['xprop', '-id', window_id, 'WM_CLASS'], stdout=PIPE)
        stdout, stderr = process.communicate()
        pmatch = re.match(b'WM_CLASS\(\w+\) = (?P<name>.+)$', stdout)
        if pmatch is not None:
            processname1, processname2 = pmatch.group('name').decode('UTF-8').split(', ')
            processname1 = processname1.strip('"')
            processname2 = processname2.strip('"')

        return {
            'windowname': windowname,
            'processname1': processname1,
            'processname2': processname2,
        }

    return {'windowname': None, 'processname1': None, 'processname2': None}


if __name__ == '__main__':
    a = get_activity_name()
    table = Table(title='Window information')
    table.add_column('Name', justify='left', style='cyan', no_wrap=True)
    table.add_column('Value', style='magenta')
    table.add_row('Window name', str(a['windowname']))
    table.add_row('Process name', str(a['processname1']))
    table.add_row('Process name', str(a['processname2']))
    table.add_row('Process1 assign', Markdown(f'assign [class="{a["processname1"]}"] → Test'))
    table.add_row('Process2 assign', Markdown(f'assign [class="{a["processname2"]}"] → Test2'))
    table.add_row('Process [bold red]Title[/bold red] assign', Markdown(f'assign [title="{a["windowname"]}"] → Title'))

    table.add_row(
        'For window1 assign', Markdown(f'for_window [class="{a["processname1"]}"] floating enable border pixel 3')
    )
    table.add_row('For window2 assign', Markdown(f'for_window [class="{a["processname1"]}"] title_format "* %title *"'))
    table.add_row(
        'For window3 assign',
        Markdown(
            f'for_window [title="{a["windowname"]}"] move to workspace $ws9, focus, move workspace to output $hdm0'
        ),
    )
    console = Console(width=120)
    console.print(table)
