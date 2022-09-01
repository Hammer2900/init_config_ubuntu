import json
import arrow
from fabric import task, Connection, Config
from rich import print, pretty, inspect
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown


# config = Config(overrides={'sudo': {'password': '123456'}})
# server = Connection(
#     config=config,
# )


@task(default=True)
def pwd(ctx):
    """Test task.

    Echo.
    """
    print('[√]: ', ctx.run('pwd'))


@task(help={'com': 'Enter docker command, example: start, stop, restart'})
def docker_redis(ctx, com='start'):
    """Run redis container commands."""
    if com == 'start':
        ctx.run('sudo docker run --rm -d --name some-redis -p 6379:6379 redis redis-server --appendonly yes')
    elif com == 'stop':
        ctx.run('sudo docker stop $(sudo docker ps -a -q --filter="name=some-redis")')


@task()
def install_exa(ctx):
    """Install exa app from github.

    Unpack zip archive.
    """
    ctx.run('wget -P /tmp/ https://github.com/ogham/exa/releases/download/v0.9.0/exa-linux-x86_64-0.9.0.zip')
    ctx.run('unzip /tmp/exa-linux-x86_64-0.9.0.zip -d /tmp/')
    ctx.sudo('cp /tmp/exa-linux-x86_64 /usr/bin/exa')
    ctx.run('exa --help')
    ctx.run('rm /tmp/exa-linux-x86_64-0.9.0.zip')
    ctx.run('rm -d -r /tmp/exa-linux-x86_64')


@task()
def install_bat(ctx):
    """Install bat app from github.

    Unpack gz archive.
    """
    ctx.run(
        'wget -P /tmp/ https://github.com/sharkdp/bat/releases/download/v0.12.1/bat-v0.12.1-x86_64-unknown-linux-gnu.tar.gz'
    )
    ctx.run('tar -xzvf /tmp/bat-v0.12.1-x86_64-unknown-linux-gnu.tar.gz -C /tmp')
    ctx.sudo('cp /tmp/bat-v0.12.1-x86_64-unknown-linux-gnu/bat /usr/bin/')
    ctx.run('bat --help')
    ctx.run('rm /tmp/bat-v0.12.1-x86_64-unknown-linux-gnu.tar.gz')
    ctx.run('rm -d -r /tmp/bat-v0.12.1-x86_64-unknown-linux-gnu')


@task()
def install_lf(ctx):
    """Install lf file manager app from github.

    Unpack gz archive.
    """
    ctx.run('wget -P /tmp/ https://github.com/gokcehan/lf/releases/download/r26/lf-linux-amd64.tar.gz')
    ctx.run('tar -xzvf /tmp/lf-linux-amd64.tar.gz -C /tmp')
    ctx.sudo('cp /tmp/lf /usr/bin/lf')
    ctx.run('lf --help')


@task(
    help={
        'ui': 'Show ui',
        'monitor': 'monitor lan network',
    }
)
def cap(ctx, monitor=False, ui=False, fb=False):
    """Install or use network sniffer."""
    if monitor:
        ctx.sudo(f'docker run --rm -it --privileged --net=host bettercap/bettercap -eval "net.probe on; ticker on"')
    elif ui:
        ctx.sudo(f'docker run --rm -it --privileged --net=host bettercap/bettercap -caplet http-ui')
    elif fb:
        with ctx.cd(f'/dev/shm/caplets/fb-phish'):
            ctx.sudo(f'docker run --rm -it --privileged --net=host bettercap/bettercap -caplet fb-phish/fb-phish')
    else:
        ctx.sudo(f'docker pull bettercap/bettercap')
        with ctx.cd(f'/dev/shm/'):
            ctx.run('git clone https://github.com/bettercap/caplets')


@task(
    help={
        'name': 'Name of virtualenv folder, example: .venv',
        'remove': 'Remove folder from memory.',
        'console': 'Run terminal and activate env.',
        'lab': 'Run jupiter lab server',
    }
)
def fastenv(ctx, name='.venv', remove=False, console=False, lab=False):
    """Prepare fast env for python 3 in memory."""
    if remove and not console:
        ctx.run(f'rm -d -r /dev/shm/{name}')
    elif not remove and console:
        ctx.run(f'export $DISPLAY && sakura -e mc')
    elif lab and not remove and not console:
        ctx.run(f'/dev/shm/{name}/bin/jupyter-lab')
    else:
        ctx.run('pip3 install --user virtualenv')
        ctx.run('virtualenv --help')
        ctx.run(f'virtualenv /dev/shm/{name} && source /dev/shm/{name}/bin/activate')
        ctx.run(f'/dev/shm/.venv/bin/python -m pip install --upgrade pip')
        ctx.run(
            f'source /dev/shm/{name}/bin/activate && pip install git+https://github.com/Hammer2900/json_help_object --upgrade'
        )
        ctx.run(f'source /dev/shm/{name}/bin/activate && pip install rich')
        ctx.run(f'source /dev/shm/{name}/bin/activate && pip install fire')
        ctx.run(f'source /dev/shm/{name}/bin/activate && pip install pip-lock')
        ctx.run(f'source /dev/shm/{name}/bin/activate && pip install pretty_errors')
        ctx.run(f'source /dev/shm/{name}/bin/activate && pip install pip install --upgrade python-box[all]')
        ctx.run(f'source /dev/shm/{name}/bin/activate && pip install pip install black')
        ctx.run(f'source /dev/shm/{name}/bin/activate && pip install pipdeptree')
        ctx.run(f'source /dev/shm/{name}/bin/activate && pip install pip-autoremove')
        ctx.run(f'source /dev/shm/{name}/bin/activate && pip install pipgrip')
        ctx.run(f'source /dev/shm/{name}/bin/activate && pip install pipreqs')
        ctx.run(f'source /dev/shm/{name}/bin/activate && pip install jupyterlab')
        ctx.run(f'source /dev/shm/{name}/bin/activate && pip list')
        ctx.run(f'mkdir -p /dev/shm/{name}/all/')
        ctx.run(
            f'wget -P /dev/shm/{name}/all/ https://raw.githubusercontent.com/google/python-fire/master/examples/widget/collector.py'
        )
        ctx.run(f'whereis python3')
        ctx.run(f'echo "source /dev/shm/{name}/bin/activate"')


@task(
    help={
        'name': 'Name of virtualenv folder, example: .venv',
        'remove': 'Remove folder from memory.',
        'console': 'Run terminal and activate env.',
    }
)
def fastenv2(ctx, name='.venv2', remove=False, console=False):
    """Prepare fast env for python 2 in memory."""
    if remove and not console:
        ctx.run(f'rm -d -r /dev/shm/{name}')
    elif not remove and console:
        ctx.run(f'export $DISPLAY && sakura -e mc')
    else:
        ctx.run(f'virtualenv --python=/usr/bin/python2 /dev/shm/{name}')
        ctx.run(f'echo "source /dev/shm/{name}/bin/activate"')
        with ctx.cd(f'/dev/shm/{name}'):
            # ctx.run('git clone https://github.com/JPaulMora/Pyrit')
            with ctx.cd(f'/dev/shm/{name}/Pyrit'):
                ctx.run(f'/dev/shm/{name}/bin/python setup.py install')
            ctx.run(f'sudo rm /usr/bin/pyrit')
            ctx.run(f'sudo ln -s /dev/shm/{name}/bin/pyrit /usr/bin/pyrit')
