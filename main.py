from emulator import *
import os
import argparse


def main():
    # парсим аргументы командной строки
    parser = argparse.ArgumentParser(description="Console emulator.")
    parser.add_argument('--vfs-root', help='Path to the physical location of the VFS.')
    parser.add_argument('--startup-script', help='Path to a startup script to execute.')

    args = parser.parse_args()

    # обновляем глобальный конфиг
    if args.vfs_root:
        config['vfs_root'] = args.vfs_root
        # если задан vfs, сразу переходим в него
        if os.path.isdir(args.vfs_root):
            os.chdir(args.vfs_root)
        else:
            print(f"warning: vfs-root directory '{args.vfs_root}' not found. Using current directory.")
            config['vfs_root'] = os.getcwd()  # используем текущую как запасной вариант

    if args.startup_script:
        config['startup_script'] = args.startup_script

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
