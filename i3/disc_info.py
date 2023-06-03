import os
import psutil
from rich.console import Console
from rich.table import Table


def get_disk_info():
    partitions = psutil.disk_partitions()
    disk_info = []

    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        label = os.path.basename(partition.mountpoint)
        disk_info.append(
            {
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'label': label,
                'fstype': partition.fstype,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent,
            }
        )

    return disk_info


def print_disk_info(disk_info):
    console = Console(width=180)
    table = Table(show_header=True, header_style='bold magenta')
    table.add_column('Device')
    table.add_column('Mountpoint')
    table.add_column('Label')
    table.add_column('File System Type')
    table.add_column('Total', justify='right')
    table.add_column('Used', justify='right')
    table.add_column('Free', justify='right')
    table.add_column('Percent', justify='right')

    for info in disk_info:
        table.add_row(
            info['device'],
            info['mountpoint'],
            info['label'],
            info['fstype'],
            f"{info['total']:,}",
            f"{info['used']:,}",
            f"{info['free']:,}",
            f"{info['percent']}%",
        )

    console.print(table)


if __name__ == '__main__':
    print_disk_info(get_disk_info())
