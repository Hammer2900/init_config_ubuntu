#!/home/izot/Documents/111/init_config_ubuntu/.env38/bin/python
import fire
from shutil import which
from pathlib import Path
import subprocess
from subprocess import Popen, PIPE, STDOUT


class EnvFinder:
    """Find and activate env in terminal for current folder."""

    def __init__(self):
        self.terminal = 'sakura'
        self.search_patterns = [
            '.env*',
            '.venv*',
        ]

    def fast(self, folder_path: str = '/dev/shm'):
        """Find or install python env to shd path."""

    def info(self):
        """Check all install programs."""
        for prog in ['sakura', 'fish', 'mc', 'python', 'python2.7', 'python3.6', 'python3.8', 'python3.9']:
            print(f'{prog}:  {which(prog)}')

    def print(self, folder_path):
        """Find and print information."""
        for lines in self.search_patterns:
            res = [next(x.glob('bin/python')) for x in Path(folder_path).glob(lines)]
            print('[-]', res)

    def find(self, folder_path: str, first: bool = True):
        """Find and run first env in dir."""
        a = Path(folder_path)
        registry = []
        for lines in self.search_patterns:
            res = [next(x.glob('bin/activate.fish')) for x in a.glob(lines)]
            registry = registry + res
        print('[111]', registry)
        if first and registry:
            Popen(
                [
                    'sakura',
                    '-e',
                    'fish',
                    '-C',
                    f'"source {registry[0]}"',
                ],
                stdin=None,
                stdout=None,
                stderr=None,
                close_fds=True,
                shell=False,
            )
        elif not first and registry:
            for lines in registry:
                Popen(
                    [
                        'sakura',
                        '-e',
                        'fish',
                        '-C',
                        f'"source {lines}"',
                    ],
                    stdin=None,
                    stdout=None,
                    stderr=None,
                    close_fds=True,
                    shell=False,
                )
        else:
            print('[error] not found')


if __name__ == '__main__':
    fire.Fire(EnvFinder)
    # sakura -e 'fish -C "source /home/izot/Documents/111/init_config_ubuntu/.env38/bin/activate.fish"'
    # Popen(
    #     [
    #         'sakura',
    #         '-e',
    #         'fish',
    #         '-C',
    #         '"source /home/izot/Documents/111/init_config_ubuntu/.env38/bin/activate.fish"',
    #     ],
    #     stdin=None,
    #     stdout=None,
    #     stderr=None,
    #     close_fds=True,
    #     shell=False,
    # )
    # a = Path('/home/izot/Documents/111/init_config_ubuntu')
    # print('[-]', [next(x.glob('bin/activate.fish')) for x in a.glob('.env*')])
    # a1 = [x for x in a.glob('.env*')]
    # print('[-]', [x for x in a1[0].glob('bin/activate.fish')])
