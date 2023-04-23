#!/run/media/izot/652aebd5-b153-4f9e-ba3d-2fb1b4d4b246/jek/TEMP/init_config_ubuntu/.venv/bin/python
import fire
from art import text2art
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich import print, pretty, inspect
from rich.console import Console
from rich.syntax import Syntax
from slugify import slugify


class UtilsCommands:
    def header(self, text: str, left: str = '/', right: str = '/', length: int = 100):
        side_size = int((length - len(text)) / 2)
        print(f'# {side_size * left} {text} {side_size * right}')

    def art_header(self, text: str, font: str = 'alligator'):
        """
        font list:
        block
        bulbhead
        digital
        ivrit
        lean
        mini
        mnemonic
        script
        shadow
        slant
        speed
        standard
        straight
        tanja
        thinkertoy
        varsity
        alligator
        :param text: text
        :param font: alligator
        """
        print(text2art(text, font=font))

    def slagify(self, text: str):
        print(slugify(text))

    def border_for_text(self, text: str):
        console = Console(width=120, record=True)
        jtext = Text(text, justify='left')
        console.print(Panel(jtext, title=text[:10], width=120, highlight=True))

    def open_terminal_with_env(self):
        ...

    def wrap_files_to_folder(self):
        ...

    def help(self):
        """
        Program Run Samples:

        Example 1:
        To use the header function, run:
        ./utils.py header "My Text"

        Example 2:
        To use the slagify function, run:
        ./utils.py slagify "My Text"

        Example 3:
        To use the border_for_text function, run:
        ./utils.py border_for_text "My Text"

        Example 4:
        To use the open_terminal_with_env function, run:
        ./utils.py open_terminal_with_env "/dev/shm"

        Example 5:
        To use the wrap_files_to_folder function, run:
        ./utils.py wrap_files_to_folder "/dev/shm"
        """
        help_text = self.help.__doc__
        syntax = Syntax(help_text, 'python', theme='ansi_dark', line_numbers=False)
        console = Console(width=120, record=True)
        # console.print("[bold]Help Information:[/bold]\n")
        console.print(syntax)


if __name__ == '__main__':
    fire.Fire(UtilsCommands)
