from pathlib import Path
import itertools as it, glob
from typing import Optional

from fabric import task, Connection, Config, Task
from rich import print, pretty, inspect
from dataclasses import dataclass, field
from pathlib import Path

server = Connection(
    # host='nixos@192.168.28.179',
    # host='nixos@192.168.28.211',
    host='izot@192.168.28.179',
    connect_kwargs={
        'password': '123456',
    },
    config=Config(overrides={'sudo': {'password': '123456'}}),
)


@dataclass
class ConfigPlanOptions:
    local_path: Path = field(default_factory=Path)
    remote_path: Path = field(default_factory=Path)
    single: bool = True
    replace: bool = False
    sudo: bool = False

    def __post_init__(self):
        self.local_path = Path(self.local_path)
        self.remote_path = Path(self.remote_path)

    def add_config(self, ctx):
        # проверить есть ли файл в удаленной директории
        #
        ctx.run('pwd')
        b = ctx.run(f'cat {self.remote_path}', warn=True)
        print('[✖]', b.failed)
        # if b.failed:
        #     ctx.run(f'mkdir -p {self.remote_path.parent}', warn=True)
        return 1

    def get_config(self, ctx):
        return 1

    def diff_config(self, ctx):
        return 1


@task(default=True)
def pwd(ctx):
    """
    fab --prompt-for-login-password -H izot@192.168.28.179 pwd
    fab -i /path/to/keyfile.pem -H izot@192.168.28.179 pwd
    """
    print(ctx)
    ctx.run('pwd')
    # ctx.run('lsblk')
    # ctx.run('df -h')
    # ctx.sudo('lsof /dev/sda')

    # ====================================== COPY ===================================== #

    # get default config
    # ctx.get('/mnt/etc/nixos/configuration.nix', '.configuration.nix')

    # put local config to server
    # ctx.put('.configuration.nix', '/dev/shm/configuration.nix')
    # ctx.sudo('cp /dev/shm/configuration.nix /mnt/etc/nixos/configuration.nix')
    # ctx.sudo('cat /mnt/etc/nixos/configuration.nix')


@task
def mbr(ctx, disc='/dev/sda', disk1='/dev/sda1', disk2='/dev/sda2'):
    ctx.sudo(f'parted {disc} --script -- mklabel msdos')
    ctx.sudo(f'parted {disc} --script -- mkpart primary 1MB -8GB')
    ctx.sudo(f'parted {disc} --script -- set 1 boot on')
    ctx.sudo(f'parted {disc} --script -- mkpart primary linux-swap -8GB 100%')

    ctx.sudo(f'mkfs.ext4 -L nixos {disk1}')
    ctx.sudo(f'mkswap -L swap {disk2}')
    ctx.sudo(f'swapon {disk2}')
    ctx.sudo('mount /dev/disk/by-label/nixos /mnt')
    ctx.sudo('nixos-generate-config --root /mnt')

    ctx.put('.configuration.nix', '/dev/shm/configuration.nix')
    ctx.sudo('cp /dev/shm/configuration.nix /mnt/etc/nixos/configuration.nix')
    ctx.sudo('cat /mnt/etc/nixos/configuration.nix')

    # ctx.sudo('rm /mnt/etc/nixos/configuration.nix')
    # ctx.sudo('nixos-install')
    # ctx.sudo('reboot')


@task
def uefi(ctx):
    ctx.sudo('parted /dev/sda --script -- mklabel gpt')
    ctx.sudo('parted /dev/sda --script -- mkpart primary 512MB -8GB')
    ctx.sudo('parted /dev/sda --script -- mkpart primary linux-swap -8GB 100%')
    ctx.sudo('parted /dev/sda --script -- mkpart ESP fat32 1MB 512MB')
    ctx.sudo('parted /dev/sda --script -- set 3 esp on')

    ctx.sudo('mkfs.ext4 -L nixos /dev/sda1')
    ctx.sudo('mkswap -L swap /dev/sda2')
    ctx.sudo('swapon /dev/sda2')
    ctx.sudo('mkfs.fat -F 32 -n boot /dev/sda3')
    ctx.sudo('mount /dev/disk/by-label/nixos /mnt')
    ctx.sudo('mkdir -p /mnt/boot')
    ctx.sudo('mount /dev/disk/by-label/boot /mnt/boot')
    ctx.sudo('nixos-generate-config --root /mnt')

    ctx.put('.configuration.nix', '/dev/shm/configuration.nix')
    ctx.sudo('cp /dev/shm/configuration.nix /mnt/etc/nixos/configuration.nix')
    ctx.sudo('cat /mnt/etc/nixos/configuration.nix')

    # ctx.sudo('rm /mnt/etc/nixos/configuration.nix')
    ctx.sudo('nixos-install')
    # ctx.sudo('reboot')


@task
def upload_config_rebuild(ctx):
    """fab upload-config-rebuild"""
    ctx.run('lscpu')
    ctx.run('lsblk')
    ctx.run('df -m /nix/store/')
    # assert False
    ctx.put('.configuration.nix', '/dev/shm/configuration.nix')
    ctx.put('copy_config.nix', '/dev/shm/copy_config.nix')
    ctx.sudo('cp /dev/shm/configuration.nix /etc/nixos/configuration.nix')
    ctx.sudo('cp /dev/shm/copy_config.nix /etc/nixos/copy_config.nix')
    # ctx.sudo('cat /mnt/etc/nixos/configuration.nix')
    ctx.sudo('nixos-rebuild switch', warn=True)


@task
def install_my_configs(ctx):
    """
    fab install-my-configs
    fab -i /path/to/keyfile.pem -H izot@192.168.28.179 install-my-configs
    fab --prompt-for-login-password -H izot@192.168.28.179 install-my-configs
    :param ctx:
    :return:
    """
    p2 = [
        ConfigPlanOptions(
            **{
                'local_path': '../../bash/fish/config.fish',
                'remote_path': '/home/izot/.config/fish/config.fish',
                'single': True,
                'replace': False,
                'sudo': False,
            }
        ),
        # ConfigPlanOptions(**{'local_path': '/', 'remote_path': '/', 'single': True, 'replace': False, 'sudo': False}),
    ]
    print('[✖]', p2)
    for lines in p2:
        print('[✖]', lines.add_config(ctx))
    # add_config(ctx, 'path', single=True, replace=True)
    # get_config(ctx, 'path', single=True, replace=True)
    # dif_config(ctx, 'path', single=True, replace=True)


if __name__ == '__main__':
    # pwd(server)
    # mbr(server)
    # mbr(server, disc='/dev/nvme0n1', disk1='/dev/nvme0n1p1', disk2='/dev/nvme0n1p2')
    upload_config_rebuild(server)
    # uefi(server)
    # install_my_configs(server)
