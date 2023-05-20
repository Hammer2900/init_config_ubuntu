#!/run/media/izot/652aebd5-b153-4f9e-ba3d-2fb1b4d4b246/jek/TEMP/init_config_ubuntu/.venv/bin/python
import os

import fire
from rich.console import Console
from rich.table import Table


class BachRC:
    def __table(self, title):
        """
        This method creates a table with a given title.

        Input:
        title: str: The title of the table.
        Output:
        table: rich.table.Table: An instance of rich.table.
        Table with the specified title and two columns 'Command' and 'Action'.
        """
        table = Table(title=title, show_header=True)
        table.add_column('Command', justify='right', style='cyan', no_wrap=True)
        table.add_column('Action', style='magenta')
        return table

    def print(self, width: int = 170):
        """
        This method opens the user's .bashrc file,
        reads the contents and prints a table of the alias and export commands in the file.

        Input:
        width: int: The width of the console in characters. (default = 170)
        Output:
        None. A table of the alias and export commands in the user's .bashrc file is printed on the console.
        """
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
