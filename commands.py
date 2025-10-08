import time
import stat
from vfs import VFSFile, VFSDirectory

start_time = time.time()


def pwd(args, vfs):
    """печатает текущий путь"""
    print(vfs.get_current_path())


def ls(args, vfs):
    """показывает содержимое текущей или указанной папки в стиле ls -l"""
    target_path = args[0] if args else '.'
    node = vfs.get_node_from_path(target_path)

    if not node:
        print(f"ls: cannot access '{target_path}': No such file or directory")
        return

    if isinstance(node, VFSFile):
        mode = stat.filemode(node.permissions)
        print(f"{mode} {node.name}")
        return

    if isinstance(node, VFSDirectory):
        children_nodes = [{'name': '.', 'node': node}, {'name': '..', 'node': node.parent or vfs.vfs_root}]
        for name, child_node in node.children.items():
            children_nodes.append({'name': name, 'node': child_node})

        for item in sorted(children_nodes, key=lambda x: x['name']):
            child_node = item['node']
            mode = stat.filemode(child_node.permissions)
            if item['name'] == '.':
                 mode = stat.filemode(node.permissions)
            elif item['name'] == '..':
                 mode = stat.filemode(node.parent.permissions if node.parent else vfs.vfs_root.permissions)

            print(f"{mode} {item['name']}")


def cd(args, vfs):
    """меняет текущую директорию"""
    if not args:
        target_node = vfs.vfs_root
    else:
        target_path = args[0]
        target_node = vfs.get_node_from_path(target_path)

    if target_node is None:
        print(f"cd: no such file or directory: {args[0]}")
    elif not isinstance(target_node, VFSDirectory):
        print(f"cd: not a directory: {args[0]}")
    else:
        vfs.current_dir = target_node


def cat(args, vfs):
    """выводит содержимое файла"""
    if not args:
        print("cat: missing operand")
        return

    for path in args:
        node = vfs.get_node_from_path(path)
        if node is None:
            print(f"cat: {path}: No such file or directory")
        elif isinstance(node, VFSDirectory):
            print(f"cat: {path}: Is a directory")
        elif isinstance(node, VFSFile):
            print(node.content)


def uptime(args, vfs):
    """показывает время работы эмулятора"""
    seconds = int(time.time() - start_time)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    print(f"emulator up for {hours:02}:{minutes:02}:{seconds:02}")


def rev(args, vfs):
    """переворачивает строки в файле или stdin"""
    if not args:
        print("rev: missing operand")
        return

    node = vfs.get_node_from_path(args[0])
    if node is None:
        print(f"rev: {args[0]}: No such file or directory")
    elif isinstance(node, VFSDirectory):
        print(f"rev: {args[0]}: Is a directory")
    elif isinstance(node, VFSFile):
        for line in node.content.splitlines():
            print(line[::-1])


def tac(args, vfs):
    """выводит строки файла в обратном порядке"""
    if not args:
        print("tac: missing operand")
        return

    node = vfs.get_node_from_path(args[0])
    if node is None:
        print(f"tac: {args[0]}: No such file or directory")
    elif isinstance(node, VFSDirectory):
        print(f"tac: {args[0]}: Is a directory")
    elif isinstance(node, VFSFile):
        for line in reversed(node.content.splitlines()):
            print(line)


def echo(args, vfs):
    """выводит аргументы на стандартный вывод"""
    print(" ".join(args))


def chmod(args, vfs):
    """изменяет права доступа к файлу или папке"""
    if len(args) != 2:
        print("chmod: missing operand")
        return

    mode_str, path = args
    node = vfs.get_node_from_path(path)

    if node is None:
        print(f"chmod: cannot access '{path}': No such file or directory")
        return

    try:
        new_permissions = int(mode_str, 8)
        node.permissions = new_permissions
    except ValueError:
        print(f"chmod: invalid mode: '{mode_str}'")


BUILTIN_COMMANDS = {
    'pwd': pwd,
    'ls': ls,
    'cd': cd,
    'cat': cat,
    'uptime': uptime,
    'rev': rev,
    'tac': tac,
    'echo': echo,
    'chmod': chmod,
}
