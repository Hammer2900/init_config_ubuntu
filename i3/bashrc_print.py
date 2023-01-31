import os

import fire
from rich.console import Console
from rich.table import Table


class BachRC:
    def __table(self, title):
        table = Table(title=title, show_header=True)
        table.add_column('Command', justify='right', style='cyan', no_wrap=True)
        table.add_column('Action', style='magenta')
        return table

    def print(self, width: int = 170):
        alias_table = self.__table('Alias')
        export_table = self.__table('Export')
        with open(f"{os.path.expanduser('~')}/.bashrc", 'r') as f:
            for line in f:
                if line.startswith('export'):
                    export_table.add_row(*line.replace('export ', '').strip().split('=', 1))
                elif line.startswith('alias'):
                    alias_table.add_row(*line.replace('alias ', '').strip().split('=', 1))
        console = Console(width=width, record=True)
        console.rule('[bold blue].bashrc')
        console.print(alias_table, justify='center')
        console.print(export_table, justify='center')


if __name__ == '__main__':
    fire.Fire(BachRC)
