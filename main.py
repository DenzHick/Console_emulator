import argparse
from emulator import Emulator

def main():
    parser = argparse.ArgumentParser(description="Console emulator.")
    parser.add_argument('--vfs-file', default='vfs.csv', help='Path to the CSV file for the VFS.')
    parser.add_argument('--startup-script', help='Path to a startup script to execute.')

    args = parser.parse_args()

    config = {
        'vfs_file': args.vfs_file,
        'startup_script': args.startup_script,
    }

    emulator = Emulator(config)

    print("--- Emulator Configuration ---")
    # для вывода конфига можно сделать специальную команду или просто распечатать
    for key, value in config.items():
        print(f"{key}={value or 'not set'}")
    print("----------------------------\n")

    emulator.repl()


if __name__ == "__main__":
    main()
