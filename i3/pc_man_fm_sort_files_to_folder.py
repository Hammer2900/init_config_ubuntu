import fire
import os
import shutil
from pathlib import Path
from datetime import datetime


def main(*paths):
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
