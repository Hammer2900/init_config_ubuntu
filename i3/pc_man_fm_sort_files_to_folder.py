#!/run/media/izot/652aebd5-b153-4f9e-ba3d-2fb1b4d4b246/jek/TEMP/init_config_ubuntu/.venv/bin/python
import fire
import os
import shutil
from pathlib import Path
from datetime import datetime


def main(*paths):
    """
    Organizes and copies files and directories to a dated and sized folder in the user's Downloads directory.

    This function takes multiple file and directory paths as input, calculates the total size and
    file types, and then copies them to a new folder in the user's Downloads directory. The new
    folder's name is based on the current date, the total size of the copied files (in MB), the
    total number of files, and the unique file extensions.

    Args:
        *paths: A variable number of arguments representing file or directory paths to be processed.
               Each argument should be a string representing a valid path.

    Example Usage:
      python your_script.py /path/to/file1.txt /path/to/directory1 /path/to/file2.pdf

    Raises:
        This function itself does not explicitly raise exceptions. The shutil.copy2 and shutil.copytree functions that it calls may raise exceptions (OSError, IOError).

    """
    today = datetime.today().strftime('%Y-%m-%d')
    home_dir = Path.home() / 'Downloads'

    # Хранение информации о уже добавленных расширениях и общих файлах
    added_extensions = set()
    total_files = 0
    total_size = 0

    for path in paths:
        source_path = Path(path)
        if source_path.exists():
            # Если путь - это файл, обновляем статистику
            if source_path.is_file():
                added_extensions.add(source_path.suffix)
                total_files += 1
                total_size += source_path.stat().st_size

            # Если путь - каталог, обновляем статистику для его содержимого
            elif source_path.is_dir():
                for folder_file in source_path.glob('**/*'):
                    if folder_file.is_file():
                        added_extensions.add(folder_file.suffix)
                        total_files += 1
                        total_size += folder_file.stat().st_size

        else:
            print(f'Путь не существует: {source_path}')

    # Формирование окончательного имени папки
    total_size_mb = total_size / (1024 * 1024)
    folder_name = f'{today}({total_size_mb:.2f}MB)({total_files})'

    # Добавление информации о расширениях
    for ext in added_extensions:
        folder_name += f"_{ext.lstrip('.')}"

    final_destination_folder = home_dir / folder_name

    # Создание окончательной папки, если еще не существует
    os.makedirs(final_destination_folder, exist_ok=True)

    # Копирование или перемещение файлов и папок в окончательную папку
    for path in paths:
        source_path = Path(path)
        if source_path.exists():
            # Если путь - это файл, копируем его
            if source_path.is_file():
                shutil.copy2(source_path, final_destination_folder)
                print(f'Копирование файла: {source_path}')

            # Если путь - каталог, копируем его содержимое
            elif source_path.is_dir():
                for folder_file in source_path.glob('**/*'):
                    if folder_file.is_file():
                        shutil.copy2(folder_file, final_destination_folder)
                        print(f'Копирование файла: {folder_file}')

        else:
            print(f'Путь не существует: {source_path}')

    print(f'Окончательное имя папки: {final_destination_folder}')


if __name__ == '__main__':
    fire.Fire(main)
