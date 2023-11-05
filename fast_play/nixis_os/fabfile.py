from pathlib import Path
import itertools as it, glob
from fabric import task, Connection, Config, Task
from rich import print, pretty, inspect

server = Connection(
    host='nixos@192.168.28.179',
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

    # ====================================== MBR ====================================== #

    # server.sudo('parted /dev/sda --script -- mklabel msdos')
    # server.sudo('parted /dev/sda --script -- mkpart primary 1MB -8GB')
    # server.sudo('parted /dev/sda --script -- mkpart primary linux-swap -8GB 100%')

    # server.sudo('mkfs.ext4 -L nixos /dev/sda1')
    # server.sudo('mkswap -L swap /dev/sda2')
    # server.sudo('swapon /dev/sda2')
    # server.sudo('mount /dev/disk/by-label/nixos /mnt')
    # server.sudo('nixos-generate-config --root /mnt')

    # server.put('.configuration.nix', '/dev/shm/configuration.nix')
    # server.sudo('cp /dev/shm/configuration.nix /mnt/etc/nixos/configuration.nix')
    # server.sudo('cat /mnt/etc/nixos/configuration.nix')

    # server.sudo('rm /mnt/etc/nixos/configuration.nix')
    # server.sudo('nixos-install')
    # server.sudo('reboot')

    # ====================================== UEFI ===================================== #

    server.sudo('parted /dev/sda --script -- mklabel gpt')
    server.sudo('parted /dev/sda --script -- mkpart primary 512MB -8GB')
    server.sudo('parted /dev/sda --script -- mkpart primary linux-swap -8GB 100%')
    server.sudo('parted /dev/sda --script -- mkpart ESP fat32 1MB 512MB')
    server.sudo('parted /dev/sda --script -- set 3 esp on')

    server.sudo('mkfs.ext4 -L nixos /dev/sda1')
    server.sudo('mkswap -L swap /dev/sda2')
    server.sudo('swapon /dev/sda2')
    server.sudo('mkfs.fat -F 32 -n boot /dev/sda3')
    server.sudo('mount /dev/disk/by-label/nixos /mnt')
    server.sudo('mkdir -p /mnt/boot')
    server.sudo('mount /dev/disk/by-label/boot /mnt/boot')
    server.sudo('nixos-generate-config --root /mnt')

    server.put('.configuration.nix', '/dev/shm/configuration.nix')
    server.sudo('cp /dev/shm/configuration.nix /mnt/etc/nixos/configuration.nix')
    server.sudo('cat /mnt/etc/nixos/configuration.nix')

    # server.sudo('rm /mnt/etc/nixos/configuration.nix')
    server.sudo('nixos-install')
    # server.sudo('reboot')


@task
def mbr(ctx):
    server.sudo('parted /dev/sda --script -- mklabel msdos')
    server.sudo('parted /dev/sda --script -- mkpart primary 1MB -8GB')
    server.sudo('parted /dev/sda --script -- mkpart primary linux-swap -8GB 100%')

    server.sudo('mkfs.ext4 -L nixos /dev/sda1')
    server.sudo('mkswap -L swap /dev/sda2')
    server.sudo('swapon /dev/sda2')
    server.sudo('mount /dev/disk/by-label/nixos /mnt')
    server.sudo('nixos-generate-config --root /mnt')

    server.put('.configuration.nix', '/dev/shm/configuration.nix')
    server.sudo('cp /dev/shm/configuration.nix /mnt/etc/nixos/configuration.nix')
    server.sudo('cat /mnt/etc/nixos/configuration.nix')

    # server.sudo('rm /mnt/etc/nixos/configuration.nix')
    server.sudo('nixos-install')
    # server.sudo('reboot')


if __name__ == '__main__':
    pwd(server)
