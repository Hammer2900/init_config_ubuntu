import sh
import fire
import os.path
from sh import Command

qemu = Command('qemu-system-x86_64')

DEFAULT_URL = '/home/izot/Downloads/nixos-minimal-23.05.4662.34bdaaf1f0b7-x86_64-linux.iso'
DEFAULT_DISC = 'nixos-hdd.qcow2'
START_TEMPLATE = [
    '-enable-kvm',
    '-smp',
    '6',
    '-m',
    '7096',
    '-boot',
    'd',
    '-cdrom',
    DEFAULT_URL,
    '-hda',
    DEFAULT_DISC,
]


class RunVm:
    def run(self):
        """Create new vm."""
        if not os.path.isfile(DEFAULT_DISC):
            sh.qemu_img('create', '-f', 'qcow2', '-o', f'{DEFAULT_DISC}', '60G')
        qemu(*START_TEMPLATE)

    def clean(self):
        """Clean all disk images."""

    def kill(self):
        """Kill any running QEMU processes."""

        pids = sh.ps("-ef") | sh.grep("qemu-system-x86_64") | sh.grep("-v", "grep") | sh.awk("{print $2}")
        print('[✖]', pids)

        if not pids:
            print("No running QEMU process found.")
            return

        for pid in pids:
            print(f"Killing QEMU process with PID: {pid}")
            sh.kill(pid)

        print("Successfully killed the QEMU process.")


def info(self):
    """Test info."""


if __name__ == '__main__':
    fire.Fire(RunVm, name='VM manager v1.0')
