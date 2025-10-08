import os
import sys
import shlex
import getpass
import socket
import argparse
import csv
import base64
from io import StringIO


# --- VFS (виртуальная файловая система) ---

class VFSNode:
    """базовый узел в vfs (файл или папка)"""

    def __init__(self, name):
        self.name = name
        self.parent = None


class VFSFile(VFSNode):
    """узел-файл"""

    def __init__(self, name, content=""):
        super().__init__(name)
        self.content = content

    def __repr__(self):
        return f"File('{self.name}')"


class VFSDirectory(VFSNode):
    """узел-папка"""

    def __init__(self, name):
        super().__init__(name)
        self.children = {}  # {'имя': VFSNode}

    def add_child(self, node):
        node.parent = self
        self.children[node.name] = node

    def __repr__(self):
        return f"Dir('{self.name}')"


# тут будет наша vfs и текущая директория
vfs_root = VFSDirectory('/')
current_dir = vfs_root


def load_vfs(vfs_path):
    """загружает vfs из csv файла в память"""
    global vfs_root, current_dir
    vfs_root = VFSDirectory('/')
    current_dir = vfs_root

    try:
        with open(vfs_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # пропускаем заголовок
            for row in reader:
                path_str, type, content = row
                path_parts = [part for part in path_str.split('/') if part]

                node = vfs_root
                # идем по пути, создавая папки, если их нет
                for part in path_parts[:-1]:
                    if part not in node.children:
                        new_dir = VFSDirectory(part)
                        node.add_child(new_dir)
                    node = node.children[part]

                # создаем сам файл или папку
                name = path_parts[-1]
                if type == 'dir':
                    if name not in node.children:
                        new_node = VFSDirectory(name)
                        node.add_child(new_node)
                elif type == 'file':
                    # декодируем контент из base64
                    decoded_content = base64.b64decode(content).decode('utf-8')
                    new_node = VFSFile(name, decoded_content)
                    node.add_child(new_node)

    except FileNotFoundError:
        print(f"warning: vfs file '{vfs_path}' not found. Using empty VFS.")
    except Exception as e:
        print(f"error loading vfs: {e}")


def get_node_from_path(path):
    """находит узел по абсолютному или относительному пути"""
    if not path:
        return current_dir

    # определяем стартовую точку: корень или текущая папка
    if path.startswith('/'):
        start_node = vfs_root
        path_parts = [part for part in path.split('/') if part]
    else:
        start_node = current_dir
        path_parts = [part for part in path.split('/') if part]

    node = start_node
    for part in path_parts:
        if part == '.':
            continue
        if part == '..':
            if node.parent:
                node = node.parent
            continue
        # ищем дочерний узел
        if isinstance(node, VFSDirectory) and part in node.children:
            node = node.children[part]
        else:
            return None  # не нашли
    return node


def get_current_path():
    """возвращает строковое представление текущего пути в vfs"""
    if current_dir == vfs_root:
        return "/"

    path = []
    node = current_dir
    while node.parent:
        path.append(node.name)
        node = node.parent
    return '/' + '/'.join(reversed(path))


# --- Конфигурация и старые функции ---

config = {
    'vfs_file': None,  # теперь это путь к файлу, а не папке
    'startup_script': None,
}


def make_prompt():
    user = getpass.getuser()
    host = socket.gethostname().split('.')[0]
    # теперь prompt всегда показывает путь внутри vfs
    short = get_current_path()
    return f"{user}@{host}:{short}$ "


def parse_command(line):
    return shlex.split(line, posix=True)


# --- Команды эмулятора (обновленные) ---

def pwd(args):
    """печатает текущий путь"""
    print(get_current_path())


def ls(args):
    """показывает содержимое текущей или указанной папки"""
    target_path = args[0] if args else '.'
    node = get_node_from_path(target_path)

    if not node:
        print(f"ls: cannot access '{target_path}': No such file or directory")
        return

    if isinstance(node, VFSFile):
        print(node.name)  # если ls на файл, просто печатаем его имя
        return

    if isinstance(node, VFSDirectory):
        # добавляем . и .. для красоты
        output = ['.', '..'] + list(node.children.keys())
        for name in sorted(output):
            print(name, end='  ')
        print()


def cd(args):
    """меняет текущую директорию"""
    global current_dir
    if not args:
        # cd без аргументов теперь ведет в корень vfs
        target_node = vfs_root
    else:
        target_path = args[0]
        target_node = get_node_from_path(target_path)

    if target_node is None:
        print(f"cd: no such file or directory: {args[0]}")
    elif not isinstance(target_node, VFSDirectory):
        print(f"cd: not a directory: {args[0]}")
    else:
        current_dir = target_node


def cat(args):
    """выводит содержимое файла"""
    if not args:
        print("cat: missing operand")
        return

    for path in args:
        node = get_node_from_path(path)
        if node is None:
            print(f"cat: {path}: No such file or directory")
        elif isinstance(node, VFSDirectory):
            print(f"cat: {path}: Is a directory")
        elif isinstance(node, VFSFile):
            print(node.content)


def conf_dump(args):
    """выводит текущую конфигурацию"""
    for key, value in config.items():
        print(f"{key}={value or 'not set'}")


# словарь для быстрого поиска команд
BUILTIN_COMMANDS = {
    'pwd': pwd,
    'ls': ls,
    'cd': cd,
    'cat': cat,
    'conf-dump': conf_dump,
}


# --- Основная логика (почти без изменений) ---

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
                clean_line = line.strip()
                if not clean_line or clean_line.startswith('#'):
                    continue

                prompt = make_prompt()
                print(prompt + clean_line)

                execute_command(clean_line)

    except FileNotFoundError:
        print(f"error: startup script not found at '{script_path}'")
    except Exception as e:
        print(f"error reading script '{script_path}': {e}")


def repl():
    """Основной цикл REPL"""
    while True:
        try:
            prompt = make_prompt()
            line = input(prompt)
            execute_command(line)
        except EOFError:
            print("\nExiting shell...")
            break
        except KeyboardInterrupt:
            print()
            continue