from emulator import *
import argparse

def main():
    # парсим аргументы командной строки
    parser = argparse.ArgumentParser(description="Console emulator.")
    # изменил --vfs-root на --vfs-file
    parser.add_argument('--vfs-file', help='Path to the CSV file for the VFS.')
    parser.add_argument('--startup-script', help='Path to a startup script to execute.')

    args = parser.parse_args()

    # обновляем глобальный конфиг
    if args.vfs_file:
        config['vfs_file'] = args.vfs_file
    if args.startup_script:
        config['startup_script'] = args.startup_script

    # загружаем vfs из файла
    if config['vfs_file']:
        load_vfs(config['vfs_file'])
    else:
        # если файл не указан, работаем с пустой vfs
        print("warning: no --vfs-file provided. Using an empty VFS.")
        load_vfs('') # вызов с пустым путем обработает ошибку

    # отладочный вывод заданных параметров
    print("--- Emulator Configuration ---")
    conf_dump([])
    print("----------------------------\n")

    # если есть скрипт, выполняем его
    if config['startup_script']:
        run_script(config['startup_script'])

    # запускаем интерактивную сессию
    repl()


if __name__ == "__main__":
    main()