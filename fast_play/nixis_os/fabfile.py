from pathlib import Path
import itertools as it, glob
from fabric import task, Connection, Config, Task
from rich import print, pretty, inspect

server = Connection(
    # host='nixos@192.168.28.179',
    host='izot@192.168.28.179',
    connect_kwargs={
        'password': '123456',
    },
)


@task(default=True)
def pwd(ctx):
    server.run('pwd')
    server.run('lsblk')
    server.run('df -h')
    # server.sudo('lsof /dev/sda')

    # ====================================== COPY ===================================== #

    # get default config
    # server.get('/mnt/etc/nixos/configuration.nix', '.configuration.nix')

    # put local config to server
    # server.put('.configuration.nix', '/dev/shm/configuration.nix')
    # server.sudo('cp /dev/shm/configuration.nix /mnt/etc/nixos/configuration.nix')
    # server.sudo('cat /mnt/etc/nixos/configuration.nix')


@task
def mbr(ctx):
    ctx.sudo('parted /dev/sda --script -- mklabel msdos')
    ctx.sudo('parted /dev/sda --script -- mkpart primary 1MB -8GB')
    ctx.sudo('parted /dev/sda --script -- mkpart primary linux-swap -8GB 100%')

    ctx.sudo('mkfs.ext4 -L nixos /dev/sda1')
    ctx.sudo('mkswap -L swap /dev/sda2')
    ctx.sudo('swapon /dev/sda2')
    ctx.sudo('mount /dev/disk/by-label/nixos /mnt')
    ctx.sudo('nixos-generate-config --root /mnt')

    ctx.put('.configuration.nix', '/dev/shm/configuration.nix')
    ctx.sudo('cp /dev/shm/configuration.nix /mnt/etc/nixos/configuration.nix')
    ctx.sudo('cat /mnt/etc/nixos/configuration.nix')

    # ctx.sudo('rm /mnt/etc/nixos/configuration.nix')
    ctx.sudo('nixos-install')
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
    server.run('lsblk')
    server.run('df -m /nix/store/')
    server.put('.configuration.nix', '/dev/shm/configuration.nix')
    server.sudo('cp /dev/shm/configuration.nix /mnt/etc/nixos/configuration.nix')


if __name__ == '__main__':
    # pwd(server)
    # mbr(server)
    upload_config_rebuild(server)
    # uefi(server)
