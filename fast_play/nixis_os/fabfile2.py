from pathlib import Path
import itertools as it, glob
from typing import Optional

from fabric import task, Connection, Config, Task
from rich import print, pretty, inspect
from dataclasses import dataclass, field
from pathlib import Path

server = Connection(
    # host='nixos@192.168.28.179',
    # host='nixos@192.168.28.186',
    host='izot@192.168.28.186',
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
    ctx.sudo('nix-collect-garbage -d')

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
    ctx.put('.configuration.nix', '/dev/shm/configuration.nix')
    ctx.put('copy_config.nix', '/dev/shm/copy_config.nix')
    ctx.sudo('cp /dev/shm/configuration.nix /etc/nixos/configuration.nix')
    ctx.sudo('cp /dev/shm/copy_config.nix /etc/nixos/copy_config.nix')
    # ctx.sudo('cat /mnt/etc/nixos/configuration.nix')
    # ctx.sudo('nixos-rebuild switch', warn=True)


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


@task
def install_nixos(ctx):
    # 1. Загружаем ваш конфиг во временную папку
    ctx.put('.configuration.nix', '/dev/shm/configuration.nix')

    # 2. Копируем его в смонтированную систему на диске
    # ВАЖНО: Копируем в /mnt/etc/nixos/, так как диск примонтирован в /mnt
    ctx.sudo('cp /dev/shm/configuration.nix /mnt/etc/nixos/configuration.nix')

    # 3. Файл hardware-configuration.nix уже там (его создал nixos-generate-config)
    ctx.sudo('ls -l /mnt/etc/nixos/')

    # 4. ЗАПУСКАЕМ УСТАНОВКУ
    # --root /mnt говорит инсталлеру, где искать новую систему
    ctx.sudo('nixos-install --no-root-passwd')

    print('Установка завершена. Можно делать reboot.')


@task
def wipe_disk(ctx, disc='/dev/sda'):
    """
    fab wipe-disk
    Полностью очищает диск перед новой установкой.
    """
    print(f'[!] ВНИМАНИЕ: Начинаем полное уничтожение данных на {disc}')

    # 1. Отключаем swap, чтобы освободить диск
    ctx.sudo('swapoff -a', warn=True)

    # 2. Принудительно отмонтируем все, что примонтировано в /mnt
    ctx.sudo('umount -R /mnt', warn=True)

    # 3. Уничтожаем подписи файловых систем (ext4, fat32, swap и т.д.)
    ctx.sudo(f'wipefs -af {disc}', warn=True)

    # 4. Забиваем нулями первый мегабайт (гарантированно убиваем MBR/GPT)
    ctx.sudo(f'dd if=/dev/zero of={disc} bs=1M count=10', warn=True)

    # 5. Сообщаем ядру, что таблица разделов изменилась
    ctx.sudo(f'partprobe {disc}', warn=True)

    print('[✔] Диск девственно чист! Теперь можно запускать таску mbr или uefi.')


@task
def search(ctx, query):
    """
    Поиск точного имени пакета в репозиториях NixOS.
    Использование: fab search spacefm
    """
    print(f"[*] Ищем '{query}' в доступных пакетах...")

    # nix-env -qaP выводит список всех пакетов с их путями (attrPath)
    # grep -i ищет без учета регистра
    # warn=True нужен, чтобы скрипт не падал, если grep ничего не найдет
    command = f"nix-env -qaP | grep -i {query}"

    result = ctx.run(command, warn=True)

    if result.failed:
        print(f"[!] По запросу '{query}' ничего не найдено.")
    else:
        print("[✔] Найденные совпадения (используй имя из левой колонки):")


if __name__ == '__main__':
    pwd(server)
    # mbr(server)
    # mbr(server, disc='/dev/nvme0n1', disk1='/dev/nvme0n1p1', disk2='/dev/nvme0n1p2')
    # upload_config_rebuild(server)
    # uefi(server)
    # install_my_configs(server)
    # install_nixos(server)
    # wipe_disk(server)
