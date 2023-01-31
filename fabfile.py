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

# server_dev = Connection(
#     host='ubuntu@11.19.14.46',
#     connect_kwargs={
#         'key_filename': KEY_PATH,
#     },
# )


@task(default=True)
def pwd(ctx):
    """Test task.

    Echo.
    """
    print('[√]: ', ctx.run('pwd'))


@task(help={'com': 'Enter docker command, example: start, stop, restart'})
def docker_redis(ctx, com='start'):
    """
    This function allows to run redis container commands.
    Args:
    com (str): Docker command, either 'start', 'stop', or 'restart'

    Returns:
    None
    """
    if com == 'start':
        ctx.run('sudo docker run --rm -d --name some-redis -p 6379:6379 redis redis-server --appendonly yes')
    elif com == 'stop':
        ctx.run('sudo docker stop $(sudo docker ps -a -q --filter="name=some-redis")')


@task()
def set_git(ctx):
    """
    This function initializes the git information for the current user. It sets the following properties:

    - User name: Tsybulskyi Evhenyi
    - User email: etsu2900@gmail.com
    - Editor: nano

    Parameters:
    - ctx (InvocationContext): The context object that is passed to the task by the task runner.

    Returns:
    None
    """
    ctx.run('git config --global user.name "Tsybulskyi Evhenyi"')
    ctx.run('git config --global user.email etsu2900@gmail.com')
    ctx.run('git config --global core.editor nano')


@task()
def copy_folder(ctx):
    """Archive folder and copy to operative memory."""
    server = Connection(
        host='ubuntu@ec21-54-158-192-99.compute-1.amazonaws.com',
        connect_kwargs={
            'key_filename': '/home/izot/Downloads/Binancekey.pem',
        },
    )
    # server.sudo('apt-get update -y')
    # server.sudo('apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y')
    server.sudo(
        'docker run -d --restart=always --name tor-socks-proxy -p 127.0.0.1:9150:9150/tcp peterdavehello/tor-socks-proxy:latest'
    )
    # server.sudo('apt install zip unzip -y')
    # server.run('zip -r /dev/shm/data.zip /home/ubuntu/projects/fr_binance_tradebot')
    # server.get('/dev/shm/data.zip', '/dev/shm/data.zip')


@task()
def install_exa(ctx):
    """
    The install_exa function is used to install the exa app from GitHub. It performs the following steps:

    Downloads the zip archive of the app from GitHub using the wget command.
    Unpacks the archive using the unzip command.
    Copies the extracted app to the /usr/bin/ directory using the sudo and cp commands.
    Verifies the installation by displaying the help information of the app using the exa --help command.
    Deletes the downloaded zip archive and the extracted app from the /tmp/ directory using the rm command.
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
    """
    Install and use network sniffer Bettercap.

    Parameters:
    monitor (bool): If True, the function will run a Bettercap command to monitor the LAN network.
    ui (bool): If True, the function will run a Bettercap command to start the Bettercap UI.
    fb (bool): If True, the function will run a Bettercap command to use the fb-phish caplet.

    Returns:
    None
    """
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


if __name__ == '__main__':
    print(
        json.dumps(
            {
                x.name.replace('_', '-'): {
                    'help': x.help,
                    'arg': [
                        {
                            'name': y.name,
                            'kind': str(y.kind),
                            'default': str(y.default),
                        }
                        for y in x.get_arguments()
                    ],
                }
                for x in locals().values()
                if isinstance(x, Task)
            }
        )
    )
