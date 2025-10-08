import os
import sys
import shlex
import getpass
import socket


# тут будем хранить конфиг
config = {
    'vfs_root': None,
    'startup_script': None,
}


def make_prompt():
    user = getpass.getuser()
    host = socket.gethostname().split('.')[0]
    home = os.path.expanduser('~')
    cwd = os.getcwd()

    # если мы в vfs, показываем путь относительно его корня
    if config['vfs_root']:
        vfs_root_abs = os.path.abspath(config['vfs_root'])
        try:
            # проверяем, находимся ли мы внутри vfs
            common_path = os.path.commonpath([vfs_root_abs, cwd])
            if common_path == vfs_root_abs:
                if cwd == vfs_root_abs:
                    short = '/'
                else:
                    short = '/' + os.path.relpath(cwd, vfs_root_abs)
            else:
                short = cwd  # мы вышли за пределы vfs
        except ValueError:
            short = cwd
    # старая логика для домашней директории
    elif cwd == home or cwd.startswith(home + os.sep):
        if cwd == home:
            short = '~'
        else:
            short = '~' + cwd[len(home):]
    else:
        short = cwd
    return f"{user}@{host}:{short}$ "


def parse_command(line):
    return shlex.split(line, posix=True)


# --- Команды эмулятора ---

def ls(args):
    print("COMMAND: ls")
    print("ARGS:", args)
    # for name in os.listdir('.'):
    #     print(name + ' ', end='')
    # print()


def cd(args):
    if len(args) == 0:
        # cd без аргументов теперь ведет в корень vfs, если он задан
        if config['vfs_root']:
            target = config['vfs_root']
        else:
            target = os.path.expanduser('~')
    else:
        target = args[0]

    try:
        # os.path.expanduser нужен для обработки '~'
        os.chdir(os.path.expanduser(target))
    except FileNotFoundError:
        print(f"cd: no such file or directory: {target}")
    except NotADirectoryError:
        print(f"cd: not a directory: {target}")
    except PermissionError:
        print(f"cd: permission denied: {target}")
    except Exception as e:
        print(f"cd: error: {e}")


def conf_dump(args):
    for key, value in config.items():
        print(f"{key}={value or 'not set'}")


# словарь для быстрого поиска команд
BUILTIN_COMMANDS = {
    'ls': ls,
    'cd': cd,
    'conf-dump': conf_dump,
}


def execute_command(line):
    """Обрабатывает одну строку с командой"""
    line = line.strip()
    if not line:
        return

    try:
        argv = parse_command(line)
    except ValueError as ve:
        print(f"parse error: {ve}")
        return

    cmd = argv[0]
    args = argv[1:]

    if cmd == 'exit':
        code = 0
        if len(args) >= 1:
            try:
                code = int(args[0])
            except ValueError:
                print("exit: numeric argument required")
                code = 1
        print("Exiting shell...")
        sys.exit(code)
    elif cmd in BUILTIN_COMMANDS:
        command_func = BUILTIN_COMMANDS[cmd]
        command_func(args)
    else:
        print(f"{cmd}: command not found")


def run_script(script_path):
    """Выполняет команды из стартового скрипта"""
    try:
        with open(script_path, 'r') as f:
            for line in f:
                # убираем пустые строки и комменты
                clean_line = line.strip()
                if not clean_line or clean_line.startswith('#'):
                    continue

                # имитируем ввод пользователя
                prompt = make_prompt()
                print(prompt + clean_line)

                execute_command(clean_line)

    except FileNotFoundError:
        print(f"error: startup script not found at '{script_path}'")
    except Exception as e:
        print(f"error reading script '{script_path}': {e}")


def repl():
    """Основной цикл REPL (Read-Eval-Print Loop)"""
    while True:
        try:
            prompt = make_prompt()
            line = input(prompt)
            execute_command(line)
        except EOFError:
            # Ctrl-D
            print("\nExiting shell...")
            break
        except KeyboardInterrupt:
            # Ctrl-C
            print()
            continue
